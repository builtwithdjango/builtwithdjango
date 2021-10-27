import { Controller } from "stimulus"
import {enter, leave} from 'el-transition';

export default class extends Controller {
    static targets = [ "projectId", "numberOfLikes", "currentUser", "modalButton", "modal" ]

    // load all likes
    connect () {
      const projectId = this.projectIdTarget.value
      const currentUserId = this.currentUserTarget.value
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

      const axios = require('axios');
      axios({
        methos: 'get',
        url: `/api/v1/like?project=${projectId}`,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        }
      })
      .then(function(response) {
        const arrayWithUsersWithLikes = response.data.filter(like => like.like == true);
        const arrayOfLikedUserIds = arrayWithUsersWithLikes.map(user => user.author);
        document.getElementById(`${projectId}_likes`).innerHTML = arrayWithUsersWithLikes.length

        if (arrayWithUsersWithLikes.length > 0 && arrayOfLikedUserIds.includes(Number(currentUserId))) {
          document.getElementById(`${projectId}_heart`).classList.add('text-red-600')
          document.getElementById(`${projectId}_heart`).classList.add('las')
          document.getElementById(`${projectId}_heart`).classList.add('la-heart')
          document.getElementById(`${projectId}_heart`).classList.add('block')
        }
        else {
          document.getElementById(`${projectId}_heart`).classList.add('lar')
          document.getElementById(`${projectId}_heart`).classList.add('la-heart')
          document.getElementById(`${projectId}_heart`).classList.add('block')
        }
      })
      .catch(error => console.log(error))
    }

    // Handle liking
    modify() {
      const projectId = this.projectIdTarget.value
      const currentUserId = this.currentUserTarget.value
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
      const numberOfLikes = Number(document.getElementById(`${projectId}_likes`).textContent)

      // get the like info for the clicked project
      const axios = require('axios');
      axios.get(`/api/v1/like?author=${this.currentUserTarget.value}&project=${this.projectIdTarget.value}`)
        .then(function (response) {
          var data = response.data

          // if there is no like action happened before we need to create one
          if (data.length == 0) {
            axios({
              method: 'post',
              url: '/api/v1/like/',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
              },
              data: {
                "author": currentUserId,
                "project": projectId,
                "like": true
              }
            })
            .then(function(response) {
              document.getElementById(`${projectId}_likes`).textContent = numberOfLikes + 1
              document.getElementById(`${projectId}_likes`).removeAttribute("class")
              document.getElementById(`${projectId}_heart`).classList.add('text-red-600')
              document.getElementById(`${projectId}_heart`).classList.add('las')
              document.getElementById(`${projectId}_heart`).classList.add('la-heart')
            })
            .catch(function(error) {
              console.log(error)
            });
          }
          // if the like is currently of, turn it on
          else if (data[0].like == false) {
            axios({
              methos: 'get',
              url: `/api/v1/like?author=${currentUserId}&project=${projectId}`,
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
              }
            })
            .then(function (response) {
              const id = response.data[0].id
              const data = {
                "author": Number(currentUserId),
                "project": Number(projectId),
                "like": true
              }
              const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
              }
              axios({
                method: 'put',
                url: `/api/v1/like/${id}/`,
                headers,
                data
              })
              .then(function(response) {
                document.getElementById(`${projectId}_likes`).innerHTML = ""
                document.getElementById(`${projectId}_likes`).innerHTML = `${numberOfLikes + 1}`
                document.getElementById(`${projectId}_heart`).removeAttribute("class")
                document.getElementById(`${projectId}_heart`).classList.add('text-red-600')
                document.getElementById(`${projectId}_heart`).classList.add('las')
                document.getElementById(`${projectId}_heart`).classList.add('la-heart')
              })
              .catch(function(error) {
                console.log(error)
              });
            })
            .catch()
          }
          // if the like is on, turn it of
          else {
            axios({
              methos: 'get',
              url: `/api/v1/like?author=${currentUserId}&project=${projectId}`,
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
              }
            })
            .then(function (response) {
              const id = response.data[0].id
              axios({
                method: 'put',
                url: `/api/v1/like/${id}/`,
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrftoken,
                },
                data: {
                  "author": currentUserId,
                  "project": projectId,
                  "like": false
                }
              })
              .then(function(response) {
                document.getElementById(`${projectId}_likes`).textContent = numberOfLikes - 1
                document.getElementById(`${projectId}_heart`).removeAttribute("class")
                document.getElementById(`${projectId}_heart`).classList.add('lar')
                document.getElementById(`${projectId}_heart`).classList.add('la-heart')
              })
              .catch(function(error) {
                console.log(error)
              });
            })
            .catch()
          }
        })
    }

    // Handle liking for unauthenticated user
    toggleModal() {
      if(this.modalTarget.classList.contains('hidden')) {
        enter(this.modalTarget)
      } else {
        leave(this.modalTarget)
      }
    }
}
