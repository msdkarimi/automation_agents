const URL = `http://127.0.0.1:8000`;

export async function get_all_payments_api() {
    try {
        const response = await fetch(URL + `/payments`)
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
