import { Controller } from "stimulus"

export default class extends Controller {
    static targets = [ "entries", "pagination" ]

    scroll() {
        let url = this.paginationTarget.querySelector("a[rel='next']").href
        var body = document.body,
            html = document.documentElement

        var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.offsetHeight)

        if (window.pageYOffset >= height - window.innerHeight - 200) {
            this.loadMore(url)
        }
    }

    loadMore(url) {
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/html',
            },
        })
        .then(response => response.text())
        .then(data => console.log("Success (text)", data))
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}