/** @odoo-module **/

import {ScheduleMenuContainer} from "./schedule_menu_container";

import {registry} from "@web/core/registry";

const systrayRegistry = registry.category("systray");

export const systrayService = {
    start() {
        systrayRegistry.add(
            "schedule_task.ScheduleMenu",
            {Component: ScheduleMenuContainer},
            {sequence: 99}
        );
    },
};
