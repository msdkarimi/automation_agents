const URL = `http://127.0.0.1:8000`;

export async function insert_new_ticket_api(new_ticket) {
    
    const response = await fetch(URL + `/tickets/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(new_ticket)
    })
    if (!response.ok) {
        let errMessage = await response.json();
        if (response.status === 422)
            errMessage = `${errMessage.errors[0].msg} for ${errMessage.errors[0].path}.`
        else
            errMessage = errMessage.error;
        throw errMessage;
    }
    else return true;
}

export async function get_all_tickets_api() {
    try {
        const response = await fetch(URL + `/tickets`)
        if (response.ok) {
            const results = await response.json()
            // console.log("from API",answer)
            return results
        } else {
            throw new Error("Application error ")
        }
    } catch (ex) {

        throw new Error("Network error " + ex)
    }
}
