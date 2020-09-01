import { Controller } from "stimulus"

export default class extends Controller {
    static targets = [ "entries", "pagination" ]

    scroll() {
        console.log('hello')
        let url = this.paginationTarget.querySelector("a[rel='next']").href
        var body = document.body,
            html = document.documentElement

        var entries = this.entriesTarget
        var pagination = this.paginationTarget

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
            
            console.log(doc.getElementById("entries"))
            console.log(typeof doc.getElementById("entries"))
            var entries = doc.getElementById("entries").children

            console.log(entries, entries.length)
            for (let entry of entries) { 
                console.log(entry);
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