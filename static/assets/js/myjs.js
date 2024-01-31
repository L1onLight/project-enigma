const COMMENT_URL = "/api/comments"
const POST_URL = "/api/posts"
const RATING_URL = "/api/rating/"

function getCsrfToken() {
    // Retrieve the CSRF token from a cookie
    const cookieValue = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieValue ? cookieValue[1] : '';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

if (window.location.pathname === "/create-post/") {
    window.addEventListener("DOMContentLoaded", function () {
        var imageInput = document.getElementById("imageInput");
        var imgElement = document.querySelector(
            ".rounded.img-fluid.shadow.w-100.fit-cover"
        );

        imageInput.addEventListener("change", function (event) {
            var file = event.target.files[0];
            var reader = new FileReader();

            reader.onload = function (e) {
                var imageUrl = e.target.result;

                imgElement.src = imageUrl;
            };

            reader.readAsDataURL(file);
        });
    });

    function capitalizeWord(word) {
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }

    window.addEventListener("DOMContentLoaded", function () {
        var postTagsInput = document.getElementById("postTags");
        var tagContainer = document.getElementById("tagContainer");
        var addTagButton = document.getElementById("addTagButton");
        var form = document.querySelector("form");
        var hiddenInputs = [];
        var errorMessage = document.getElementById("errorMessage");
        var tagTexts = [];

        addTagButton.addEventListener("click", function (event) {
            event.preventDefault();

            var tags = capitalizeWord(postTagsInput.value.trim());

            if (tags !== "") {
                if (tagTexts.includes(tags)) {
                    errorMessage.textContent = "Tag already exists";
                    return;
                }
                var div = document.createElement("span");
                div.className = "search-tag tag mx-1";
                div.innerHTML = `${tags} <i class="fa-solid fa-xmark"></i>`;

                div.addEventListener("click", function () {
                    tagContainer.removeChild(div);
                    removeHiddenInput(tags);
                });

                if (tagContainer.childElementCount >= 4) {
                    errorMessage.textContent = "You can't add more than 4 tags";
                    return;
                }

                tagContainer.appendChild(div);

                postTagsInput.value = "";

                var input = document.createElement("input");
                input.type = "hidden";
                input.name = "tags";
                input.value = tags;
                hiddenInputs.push(input);
                form.appendChild(input);

                tagTexts.push(tags);

                errorMessage.textContent = "";
            }
        });

        function removeHiddenInput(tags) {
            hiddenInputs = hiddenInputs.filter(function (input) {
                if (input.value === tags) {
                    form.removeChild(input);
                    return false;
                }
                return true;
            });

            tagTexts = tagTexts.filter(function (tag) {
                return tag !== tags;
            });
        }
    });
}

function createProfileAside(user) {
    const overlay = document.createElement("div");
    overlay.classList.add("overlay");

    const aside = document.createElement("aside");
    aside.classList.add("profile-card", "shadow", "p-2");

    if (user.username !== null)
        username_if = `<h5><a href="/user/${user.id}" class="link-card">${user.username}</a></h5>`;
    else username_if = ``;
    if (
        user.first_name !== null &&
        user.last_name !== null &&
        user.first_name !== "" &&
        user.last_name !== ""
    ) {
        lastname = `${user.first_name} ${user.last_name}`;
    } else if (username_if !== ``) {
        lastname = username_if;
    } else if (user.first_name !== null) {
        lastname = user.first_name;
    } else if (user.last_name !== null) {
        lastname = user.last_name;
    }
    if (username_if === `` && lastname === ``) {
        username_if = "Profile not configured";
    }

    if (user.inst_url)
        inst_url = `<a href="${user.inst_url}" target="_blank"><i class="fa-brands fa-instagram fa-xl p-2 pb-4 link-card-icons" style="color: #df437e"></i>`;
    else inst_url = ``;
    if (user.steam_url)
        steam_url = `<a href="${user.steam_url}" target="_blank"><i class="fa-brands fa-steam fa-xl p-2 pb-4 link-card-icons" style="color: #171a21"></i></a>`;
    else steam_url = ``;
    if (user.telegram_url)
        telegram_url = `<a href="${user.telegram_url}" target="_blank"><i class="fa-brands fa-telegram fa-xl p-2 pb-4 link-card-icons" style="color: #229ED9;"></i></a>`;
    else telegram_url = ``;
    aside.innerHTML = `
        <div>
          <header class="header-main pt-3">
            <a href="/user/${user.id}">
              <img src="${user.avatar}" class="unselectable" alt="">
            </a>
            <h2>${lastname}</h2>
            <h5><a href="/user/${user.id}" class="link-card">${username_if}</a></h5>
            
          </header>
          <div class="bio ps-4 pe-4">
            <p>${user.bio}</p>
          </div>
          <div class="d-flex justify-content-center">
            </a>
            ${inst_url}
            ${steam_url}
            ${telegram_url}
            
          </div>
        </div>
      `;

    overlay.appendChild(aside);

    document.body.appendChild(overlay);

    document.addEventListener("click", function (event) {
        if (
            !aside.contains(event.target) &&
            !event.target.matches('a[onclick^="fetch_id"]')
        ) {
            overlay.remove();
        }
    });
}

function fetch_id(userId) {
    const apiUrl = `/api/user/${userId}?format=json`;

    function fetch_id(userId, event) {
        event.preventDefault();
    }

    fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
            createProfileAside(data);
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function like_post(button, postId, method, _type) {

    const rating = document.getElementById(`${_type}-${postId}`);
    fetch(RATING_URL, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            "X-CSRFToken": getCsrfToken(),

        },
        body: JSON.stringify({
            "pk": postId,
            "method": method,
            "type": _type,
        })
    })
        .then((response) => {
            if (response.status === 401) {
                window.location.replace("/login/");
                return;
            }
            if (response.ok) {
                return response.text();
            } else {
                throw new Error("Failed to like the post.");
            }
        })
        .then((responseContent) => {
            const items = JSON.parse(responseContent);
            if (responseContent === "/login/") {
                window.location.replace("/login/");
                return;
            }
            console.log()
            const tl = items["total_likes"];
            console.log("TOTAL_LIKES:", tl)
            if (method === "like") {
                dislikeB = button.nextElementSibling.nextElementSibling;
                if (dislikeB.classList.contains("ratingR-1")) {
                    dislikeB.classList.remove("ratingR-1");
                }
            } else if (method === "dislike") {
                likeB = button.previousElementSibling.previousElementSibling;
                if (likeB.classList.contains("ratingG-1")) {
                    likeB.classList.remove("ratingG-1");
                }
            }
            console.log(1, button)
            if (method === "dislike") {
                button.classList.toggle("ratingR-1")
            } else if (method === "like") {
                button.classList.toggle("ratingG-1")
            }
            // button.classList.toggle(className);
            rating.innerHTML = tl;
            if (rating.innerText)
                num = +tl;
            if (num === 0) {
                rating.classList.remove("ratingG-1");
                rating.classList.remove("ratingR-1");
            } else if (num > 0) {
                rating.classList.remove("ratingR-1");
                rating.classList.add("ratingG-1");
            } else if (num < 0) {
                rating.classList.remove("ratingG-1");
                rating.classList.add("ratingR-1");
            }
        })
        .catch((error) => {
            console.error("An error occurred while liking the post:", error);
        });
}

function deleteComPost(type, id) {
    let csrftoken = getCsrfToken();
    console.log(csrftoken)
    confirmation = confirm(`Are you want do delete this ${type}?`);

    if (confirmation && type === "comment") {
        let url = `${COMMENT_URL}/${id}/`;
        fetch(url, {
            method: "DELETE",
            headers: {"X-CSRFToken": csrftoken,},
        })
            .then((response) => {
                if (response.ok) {
                    card = document.getElementById(`comment-card-${id}`);
                    card.remove();
                    location.reload()
                    return;
                } else {
                    throw new Error(`Failed to delete the post.`);
                }
            })

    } else if (confirmation && type === "post") {
        let url = `${POST_URL}/${id}/`;
        fetch(url, {
            method: "DELETE",
            headers: {"X-CSRFToken": csrftoken,},
        })
            .then((response) => {
                if (response.ok) {
                    card = document.getElementById(`post-card-${id}`);
                    card.remove();
                    location.reload()
                    return;
                } else {
                    throw new Error("Failed to delete the post.");
                }
            })

    }
}
