/** @odoo-module **/

import {registry} from "@web/core/registry";
import {systrayService} from "@schedule_task/js/systray_service";

const serviceRegistry = registry.category("services");
serviceRegistry.add("schedule_systray_service", systrayService);
