import math
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from robots.models import RiskEvent, RobotComponent, RobotGroup


ROBOT_GROUPS = [
    {"key": "hop", "name": "hop", "total": 655},
    {"key": "reuse", "name": "reuse", "total": 331},
    {"key": "254/214", "name": "254/214", "total": 965},
    {"key": "engine", "name": "engine", "total": 88},
]


def clamp(value, min_value, max_value):
    return min(max_value, max(min_value, value))


def hash_string(text: str) -> int:
    # FNV-1a 32-bit
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def mulberry32(seed: int):
    t = seed & 0xFFFFFFFF

    def rand():
        nonlocal t
        t = (t + 0x6D2B79F5) & 0xFFFFFFFF
        x = t
        x = (x ^ (x >> 15)) * (x | 1) & 0xFFFFFFFF
        x ^= (x + ((x ^ (x >> 7)) * (x | 61) & 0xFFFFFFFF)) & 0xFFFFFFFF
        x = x ^ (x >> 14)
        return (x & 0xFFFFFFFF) / 4294967296

    return rand


def pad_number(number: int, length: int) -> str:
    return str(number).zfill(length)


def pick(rand, items):
    return items[int(rand() * len(items))]


CHECK_KEYS = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
CHECK_LABELS = {
    "A1": "供电/线束",
    "A2": "温度/散热",
    "A3": "通信/网络",
    "A4": "传感器/对位",
    "A5": "抓手/执行器",
    "A6": "控制/程序",
    "A7": "安全/急停",
}


def derive_risk_level(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def create_reference_no(rand) -> str:
    base = timezone.now().date()
    end_offset = 5 + int(rand() * 25)
    start_offset = end_offset + 8 + int(rand() * 45)
    start = base - timedelta(days=start_offset)
    end = base - timedelta(days=end_offset)
    return f"{start.strftime('%y%m%d')}-{end.strftime('%y%m%d')}"


def create_part_no(rand) -> str:
    prefix = pick(rand, ["UB41", "UB42", "UA20", "UD18", "UX07"])
    section = pad_number(1 + int(rand() * 99), 3)
    family = pick(rand, ["RB", "RC", "RD", "RE"])
    suffix = pad_number(1 + int(rand() * 180), 3)
    return f"{prefix}_{section}{family}_{suffix}"


def create_tech(rand) -> str:
    pool = ["抓手", "涂胶", "焊接", "拧紧", "涂装", "码垛", "搬运", "检测", "打标"]
    first = pick(rand, pool)
    second = pick(rand, pool)
    if second == first:
        second = pick(rand, pool)
    return f"{first} + {second}" if rand() < 0.55 else first


def create_type_spec(rand) -> str:
    return pick(
        rand,
        [
            "KR600_R2830_Fortec",
            "KR210_R3100_Quantec",
            "KR120_R2700_Quantec",
            "IRB_6700_205_2.75",
            "FANUC_M_900iB_700",
            "Kawasaki_RS080N",
            "UR10e_1300",
            "Yaskawa_GP225",
        ],
    )


def build_robot_id(group_key: str, index: int) -> str:
    prefix = group_key.replace("/", "-").upper()
    return f"{prefix}-{pad_number(index + 1, 4)}"


def derive_status(rand) -> str:
    r = rand()
    if r < 0.78:
        return "online"
    if r < 0.9:
        return "maintenance"
    return "offline"


def create_checks(rand, risk_score: int, motor_temp: int, network_latency: int, battery: int) -> dict:
    base_fail_rate = 0.18 if risk_score >= 90 else 0.12 if risk_score >= 80 else 0.06
    temp_bias = 0.12 if motor_temp >= 88 else 0
    latency_bias = 0.10 if network_latency >= 280 else 0
    low_battery_bias = 0.08 if battery <= 15 else 0

    checks = {}
    for key in CHECK_KEYS:
        fail_rate = base_fail_rate
        if key == "A2":
            fail_rate += temp_bias
        if key == "A3":
            fail_rate += latency_bias
        if key == "A1":
            fail_rate += low_battery_bias

        ok = rand() >= fail_rate
        checks[key] = {"ok": ok, "label": CHECK_LABELS[key]}

    if risk_score >= 80 and all(item["ok"] for item in checks.values()):
        preferred = "A2" if motor_temp >= 88 else "A3" if network_latency >= 280 else "A6"
        checks[preferred]["ok"] = False

    return checks


def create_component(group: RobotGroup, index: int) -> RobotComponent:
    seed = hash_string(f"{group.key}::{index}")
    rand = mulberry32(seed)

    status = derive_status(rand)
    model = pick(rand, ["R-Atlas", "R-Nova", "R-Kite", "R-Edge"])

    base_battery = int(round(15 + rand() * 85))
    battery = clamp(int(round(base_battery * (0.25 + rand() * 0.45))) if status == "offline" else base_battery, 0, 100)
    base_health = int(round(62 + rand() * 38))
    health = clamp(base_health - int(round(5 + rand() * 15)) if status == "maintenance" else base_health, 0, 100)
    motor_temp = clamp(int(round(52 + rand() * 44 + (6 if status == "maintenance" else 0))), 35, 98)
    network_latency = clamp(int(round(20 + rand() * 330 + (160 if status == "offline" else 0))), 10, 500)

    last_seen_minutes_ago = int(round(rand() * (40 if status == "online" else 320)))
    last_seen = timezone.now() - timedelta(minutes=last_seen_minutes_ago)

    score = (
        30
        + (100 - health) * 0.55
        + (30 - battery) * 0.7
        + (20 if status == "offline" else 0)
        + (8 if motor_temp >= 88 else 0)
        + (8 if network_latency >= 280 else 0)
        + rand() * 12
    )
    risk_score = clamp(int(round(score)), 0, 100)
    risk_level = derive_risk_level(risk_score)
    level = "H" if risk_score >= 85 else "M" if risk_score >= 65 else "L"

    history = []
    history_count = (1 + int(rand() * 3)) if rand() < 0.22 else 0
    for h in range(history_count):
        past_hours = 8 + int(round(rand() * 120))
        event_time = timezone.now() - timedelta(hours=past_hours)
        event_score = clamp(int(round(risk_score - 10 + rand() * 25)), 40, 100)
        history.append(
            {
                "id": f"{seed}-{h}",
                "time": event_time.isoformat(),
                "score": event_score,
                "level": derive_risk_level(event_score),
            }
        )

    reason = (
        "长时间离线"
        if status == "offline"
        else "电量过低"
        if battery <= 12
        else "健康度偏低"
        if health <= 70
        else "网络时延异常"
        if network_latency >= 280
        else "电机温度偏高"
        if motor_temp >= 88
        else pick(
            mulberry32(hash_string(build_robot_id(group.key, index)) ^ 0x9E3779B9),
            ["运动控制异常", "定位漂移", "急停触发次数偏多", "传感器数据波动"],
        )
    )

    remark_hints = []
    if motor_temp >= 88:
        remark_hints.append("温度相关可能")
    if network_latency >= 280:
        remark_hints.append("通信波动")
    if battery <= 15:
        remark_hints.append("低电量影响")
    attention = "重点关注" if risk_score >= 90 else "需留意观察" if risk_score >= 80 else "观察"
    hint_text = f"{'，'.join(remark_hints)}，{attention}" if remark_hints else attention
    remark = f"{reason}；{hint_text}"

    checks = create_checks(rand, risk_score, motor_temp, network_latency, battery)

    return RobotComponent(
        group=group,
        robot_id=build_robot_id(group.key, index),
        name=f"{model} #{pad_number(index + 1, 4)}",
        part_no=create_part_no(rand),
        reference_no=create_reference_no(rand),
        type_spec=create_type_spec(rand),
        tech=create_tech(rand),
        mark=0,
        remark=remark,
        checks=checks,
        level=level,
        status=status,
        battery=battery,
        health=health,
        motor_temp=motor_temp,
        network_latency=network_latency,
        last_seen=last_seen,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_history=history,
    )


def seed_risk_events(groups, total_events: int = 240):
    reasons = ["电量过低", "健康度偏低", "网络时延异常", "电机温度偏高", "运动控制异常", "定位漂移"]
    statuses = ["pending", "acknowledged", "resolved"]
    severities = ["critical", "high", "medium", "low"]

    components = list(RobotComponent.objects.select_related("group").all())
    if not components:
        return

    rand = mulberry32(hash_string("risk-events"))
    events = []
    for i in range(total_events):
        component = components[int(rand() * len(components))]
        hours_ago = int(round(rand() * 72))
        triggered_at = timezone.now() - timedelta(hours=hours_ago, minutes=int(round(rand() * 60)))
        severity = pick(rand, severities)
        status = pick(rand, statuses)
        reason = pick(rand, reasons)
        score = clamp(int(round(55 + rand() * 45 + (15 if severity == "critical" else 0))), 0, 100)

        events.append(
            RiskEvent(
                component=component,
                group=component.group,
                robot_id=component.robot_id,
                robot_name=component.name,
                message=f"风险事件：{reason}",
                reason=reason,
                severity=severity,
                status=status,
                risk_score=score,
                triggered_at=triggered_at,
            )
        )

    RiskEvent.objects.bulk_create(events, batch_size=2000)


class Command(BaseCommand):
    help = "Seed robot groups/components/risk events into database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing robot platform data before seeding.",
        )
        parser.add_argument(
            "--events",
            type=int,
            default=240,
            help="Number of risk events to create (default: 240).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = bool(options["reset"])
        event_count = int(options["events"])

        if reset:
            RiskEvent.objects.all().delete()
            RobotComponent.objects.all().delete()
            RobotGroup.objects.all().delete()

        if RobotComponent.objects.exists() and not reset:
            self.stdout.write(self.style.WARNING("Robot components already exist; skip seeding (use --reset to recreate)."))
            return

        groups = {}
        for spec in ROBOT_GROUPS:
            group, _ = RobotGroup.objects.update_or_create(
                key=spec["key"],
                defaults={"name": spec["name"], "expected_total": spec["total"]},
            )
            groups[spec["key"]] = group

        components = []
        for spec in ROBOT_GROUPS:
            group = groups[spec["key"]]
            for index in range(spec["total"]):
                components.append(create_component(group, index))

        RobotComponent.objects.bulk_create(components, batch_size=2000)
        seed_risk_events(groups, total_events=event_count)

        self.stdout.write(self.style.SUCCESS(f"Seeded groups={len(ROBOT_GROUPS)}, components={len(components)}, events={event_count}"))

