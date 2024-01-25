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

function like_post(button, postId, method, type) {
    if (type === "post") {
        var url = `/api/like-post/${postId}/${method}`;
    } else if (type === "comment") {
        var url = `/api/like-comment/${postId}/${method}`;
    }
    var rating = document.getElementById(`${type}-${postId}`);
    fetch(url, {
        headers: {
            "Content-Type": "application/json",
        },
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
            const items = responseContent.split("|");
            if (responseContent === "/login/") {
                window.location.replace("/login/");
                return;
            }

            const className = items[0]; // Get the first item (e.g., 'ratingG-1')
            const tl = items[1]; // Get the second item (total likes count)

            // Use className and tl as needed
            // console.log('Class Name:', className);
            // console.log('Total Likes:', tl);
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

            button.classList.toggle(className);
            rating.innerHTML = tl;
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
    confirmation = confirm(`Are you want do delete this ${type}?`);

    if (confirmation && type === "comment") {
        var url = `/api/delete-comment/${id}/`;
        fetch(url, {
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error("Failed to like the post.");
                }
            })
            .then((responseContent) => {
                c = responseContent;
                if (c === '"OK"') {
                    card = document.getElementById(`comment-card-${id}`);
                    card.remove();
                }
            });
    } else if (confirmation && type === "post") {
        var url = `/api/delete-post/${id}/`;
        fetch(url, {
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error("Failed to like the post.");
                }
            })
            .then((responseContent) => {
                c = responseContent;
                if (c === '"OK"') {
                    card = document.getElementById(`post-card-${id}`);
                    card.remove();
                }
            });
    }
}
