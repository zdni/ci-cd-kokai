/** @odoo-module **/

import {registry} from "@web/core/registry";

import {useService} from "@web/core/utils/hooks";

const {Component, useState} = owl;

export class SchedulesTable extends Component {
    setup() {
        this.docs = useState({});
        this.collapse = false;
        this.orm = useService("orm");
        this.schedules = [];
    }
    _getScheduleData() {
        const records = this.env.model.root.data.schedule_ids.records;
        const schedules = [];
        for (var i = 0; i < records.length; i++) {
            schedules.push(records[i].data);
        }
        return schedules;
    }
    onToggleCollapse(ev) {
        var $panelHeading = $(ev.currentTarget).closest(".panel-heading");
        if (this.collapse) {
            $panelHeading.next("div#collapse1").hide();
        } else {
            $panelHeading.next("div#collapse1").show();
        }
        this.collapse = !this.collapse;
    }
}

SchedulesTable.template = "schedule_task.Collapse";
registry.category("fields").add("form.schedule_task", SchedulesTable);
