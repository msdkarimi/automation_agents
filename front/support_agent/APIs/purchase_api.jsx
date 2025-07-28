const URL = `http://127.0.0.1:8000`;

export async function insert_new_purchas_api(new_purchases) {
    
    const response = await fetch(URL + `/purchases/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(new_purchases)
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
