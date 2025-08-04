export class Item {
    constructor(id=null, item_id, item_name, item_description) {
        this.id = id
        this.item_id = item_id
        this.item_name = item_name
        this.item_description = item_description

    }
}

export class Purchase {
    constructor(id=null, purchase_id, customer_id, purchase_status, purchased_item_id) {
        this.id = id
        this.purchase_id = purchase_id
        this.customer_id = customer_id
        this.purchase_status = purchase_status
        this.purchased_item_id = purchased_item_id

    }
}


export class Ticket {
    constructor(id=null, customer_id, customer_comment, status, subject, date_received, date_addressed) {
        this.id = id
        this.customer_id = customer_id
        this.customer_comment = customer_comment
        this.status = status
        this.subject = subject
        this.date_received = date_received
        this.date_addressed = date_addressed
    }
}

export class AgentActions {
    constructor(the_id, is_start, is_end, think=[], chat=[], tool=[]) {
        this.the_id = the_id
        this.is_start = is_start
        this.is_end = is_end
        this.think = think
        this.chat = chat
        this.tool = tool
    }
}
