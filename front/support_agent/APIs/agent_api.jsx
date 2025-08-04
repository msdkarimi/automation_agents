const URL = `http://127.0.0.1:8000`;


export async function start_chat_with_case_context_agent(ticket_id, customer_id, customer_comment) {

    const ticket = {'ticket_id':ticket_id, 'customer_id':customer_id, 'customer_comment':customer_comment}

     const response = await fetch(URL + `/agents/case_context`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(ticket)
    })
    if (!response.ok) {
        let errMessage = await response.json();
        
        if (response.status === 422)
            errMessage = `${errMessage.errors[0].msg} for ${errMessage.errors[0].path}.`
        else
            errMessage = errMessage.error;
        throw errMessage;
    }
    else{
        const prompt_id = await response.json();
        // console.log(prompt_id.request_id)
        const es = new EventSource(URL + `/agents/case_context/stream/${prompt_id.request_id}`)
        return es
    }
}

// export async function start_chat_with_case_context_agent (ticket_id, customer_id, customer_comment) {



// }