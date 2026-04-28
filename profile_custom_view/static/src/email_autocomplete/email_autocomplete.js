/** @odoo-module **/
import { Component, mount, useRef, useState } from "@odoo/owl";

class EmailAutocomplete extends Component {
    static template = "mi_modulo.EmailAutocomplete";
    static props = {
        suggestions: Array,
        onSelect: Function,
    };
}

class EmailWidget extends Component {
    static template = "mi_modulo.EmailWidget";
    static components = { EmailAutocomplete };

    domains = [
        'gmail.com',
        'hotmail.com',
        'yahoo.com',
        'outlook.com',
        'icloud.com',
    ];

    setup() {
        this.state = useState({ suggestions: [] });
        this.emailInput = useRef("emailInput");
    }

    onInput(ev) {
        const value = ev.target.value;
        if (value.includes('@')) {
            const [local, partial] = value.split('@');
            this.state.suggestions = this.domains
                .filter(d => d.startsWith(partial))
                .map(d => `${local}@${d}`);
        } else {
            this.state.suggestions = [];
        }
    }

    onSelect(suggestion) {
        this.emailInput.el.value = suggestion;
        this.state.suggestions = [];
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const target = document.getElementById('email_widget_mount');
    if (target) {
        mount(EmailWidget, target);
    }
});
