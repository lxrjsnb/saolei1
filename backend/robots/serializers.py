from rest_framework import serializers

from .models import RobotGroup, RobotComponent, RiskEvent


class RobotGroupSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = RobotGroup
        fields = ("id", "key", "name", "expected_total", "stats")

    def get_stats(self, obj: RobotGroup):
        stats = getattr(obj, "_stats", None)
        if stats is not None:
            return stats
        return {
            "total": obj.components.count(),
            "online": obj.components.filter(status="online").count(),
            "offline": obj.components.filter(status="offline").count(),
            "maintenance": obj.components.filter(status="maintenance").count(),
            "highRisk": obj.components.filter(level="H").count(),
            "historyHighRisk": obj.components.exclude(risk_history=[]).count(),
        }


class RobotComponentSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="group.key", read_only=True)
    partNo = serializers.CharField(source="part_no")
    referenceNo = serializers.CharField(source="reference_no")
    typeSpec = serializers.CharField(source="type_spec")
    number = serializers.IntegerField()
    motorTemp = serializers.IntegerField(source="motor_temp")
    networkLatency = serializers.IntegerField(source="network_latency")
    riskScore = serializers.IntegerField(source="risk_score")
    riskLevel = serializers.CharField(source="risk_level")
    riskHistory = serializers.JSONField(source="risk_history")
    lastSeen = serializers.DateTimeField(source="last_seen")
    isHighRisk = serializers.BooleanField(source="is_high_risk", read_only=True)

    class Meta:
        model = RobotComponent
        fields = (
            "id",
            "group",
            "robot_id",
            "name",
            "partNo",
            "referenceNo",
            "number",
            "typeSpec",
            "tech",
            "mark",
            "remark",
            "checks",
            "level",
            "status",
            "battery",
            "health",
            "motorTemp",
            "networkLatency",
            "riskScore",
            "riskLevel",
            "riskHistory",
            "lastSeen",
            "isHighRisk",
        )


class RiskEventSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="group.key", read_only=True)

    class Meta:
        model = RiskEvent
        fields = (
            "id",
            "robot_id",
            "robot_name",
            "group",
            "message",
            "reason",
            "severity",
            "status",
            "risk_score",
            "notes",
            "triggered_at",
        )
