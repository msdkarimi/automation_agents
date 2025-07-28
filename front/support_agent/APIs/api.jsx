const URL = `http://127.0.0.1:8000`;


export async function send_message_to_agent(aid) {
  try {
      const response = await fetch(URL + `/agent/invoke`)
      if (response.ok) {
          const answer = await response.json()
          console.log("from API",answer)
          return answer
      } else {
          throw new Error("Application error ")
      }
  } catch (ex) {

      throw new Error("Network error " + ex)
  }
}

export async function insert_new_item_api(new_item) {
    const response = await fetch(URL + `/items/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(new_item)
    })
    if (!response.ok) {
        let errMessage = await response.json();
        if (response.status === 422)
            errMessage = `${errMessage.errors[0].msg} for ${errMessage.errors[0].path}.`
        else
            errMessage = errMessage.error;
        throw errMessage;
    }
    else return null;
}
