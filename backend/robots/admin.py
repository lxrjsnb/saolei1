from django.contrib import admin

from .models import RobotGroup, RobotComponent, RiskEvent


@admin.register(RobotGroup)
class RobotGroupAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "expected_total", "updated_at")
    search_fields = ("key", "name")


@admin.register(RobotComponent)
class RobotComponentAdmin(admin.ModelAdmin):
    list_display = (
        "robot_id",
        "part_no",
        "reference_no",
        "type_spec",
        "tech",
        "mark",
        "level",
        "status",
        "risk_level",
        "risk_score",
        "last_seen",
        "updated_at",
    )
    list_filter = ("group", "status", "level", "risk_level")
    search_fields = ("robot_id", "name", "part_no", "reference_no", "type_spec", "tech", "remark")


@admin.register(RiskEvent)
class RiskEventAdmin(admin.ModelAdmin):
    list_display = ("robot_id", "severity", "status", "risk_score", "triggered_at", "updated_at")
    list_filter = ("group", "severity", "status")
    search_fields = ("robot_id", "robot_name", "message", "reason", "notes")

