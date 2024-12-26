/** @odoo-module **/

// ensure components are registered beforehand.
import {getMessagingComponent} from "@mail/utils/messaging_component";

const {Component} = owl;

export class ScheduleMenuContainer extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.env.services.messaging.modelManager.messagingCreatedPromise.then(() => {
            this.scheduleMenuView =
                this.env.services.messaging.modelManager.messaging.models.ScheduleMenuView.insert();
            this.render();
        });
    }
}

Object.assign(ScheduleMenuContainer, {
    components: {ScheduleMenuView: getMessagingComponent("ScheduleMenuView")},
    template: "schedule_task.ScheduleMenuContainer",
});
