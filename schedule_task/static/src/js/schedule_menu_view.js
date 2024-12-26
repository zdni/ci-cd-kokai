/** @odoo-module **/

import {registerMessagingComponent} from "@mail/utils/messaging_component";
import {useComponentToModel} from "@mail/component_hooks/use_component_to_model";

const {Component} = owl;

export class ScheduleMenuView extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        useComponentToModel({fieldName: "component"});
    }
    /**
     * @returns {ScheduleMenuView}
     */
    get scheduleMenuView() {
        return this.props.record;
    }
}

Object.assign(ScheduleMenuView, {
    props: {record: Object},
    template: "schedule_task.ScheduleMenuView",
});

registerMessagingComponent(ScheduleMenuView);
