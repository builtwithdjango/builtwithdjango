import { Controller } from "stimulus"

export default class extends Controller {
    static targets = [ "entries", "pagination" ]

    scroll() {
        let next_page = this.paginationTarget.querySelector("a[rel='next']")
        if (next_page == null) { return }

        let url = next_page.href

        var body = document.body
        var html = document.documentElement

        let entries = this.entriesTarget
        let pagination = this.paginationTarget

        var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.offsetHeight)

        if (window.pageYOffset >= height - window.innerHeight) {
            this.loadMore(url, entries, pagination)
        }
    }

    loadMore(url, toAddLocation, pageLinks) {
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/html',
            },
        })
        .then(response => response.text())
        .then(data => {
            var doc = new DOMParser().parseFromString(data, "text/html")

            // Square brakcets and ... are to "freeze" HTML collection to an Array
            var entries = [...doc.getElementById("entries").children]

            for (let entry of entries) {
                toAddLocation.appendChild(entry)
            }

            // Insert pagination from new page. Since next time we want to use next which points to page 3
            var pagination = doc.getElementById("pagination").innerHTML
            pageLinks.innerHTML = pagination;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}
