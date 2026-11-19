const API_URL = "/api/posts/";

let nextPage = null;
let currentCategory = "";
let currentSearch = "";
let authMode = "login";

// CSRF TOKEN
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

// GET CSRF COOKIE
async function setupCSRF() {
    await fetch("/api/accounts/csrf/", {
        credentials: "same-origin"
    });
}

// LOAD BLOGS
async function fetchBlogs(url = API_URL, append = false) {
    const container = document.getElementById("blogContainer");

    if (!append) container.innerHTML = "<p>Loading stories...</p>";

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Unable to load blogs");

        const data = await response.json();
        const posts = data.results || data;

        nextPage = data.next || null;

        if (!append) container.innerHTML = "";

        if (posts.length === 0 && !append) {
            container.innerHTML = "<p>No blogs found.</p>";
        }

        posts.forEach(post => {
            const card = document.createElement("article");
            card.className = "blog-card";
            card.style.cursor = "pointer";

            card.addEventListener("click", () => {
                window.location.href =
                    `/post.html?slug=${encodeURIComponent(post.slug)}`;
            });

            const image = document.createElement("img");
            image.className = "blog-image";
            image.src = post.cover_image ||
                "https://placehold.co/600x400?text=BlogSpace";
            image.alt = post.title;

            const info = document.createElement("div");
            info.className = "blog-info";

            const category = document.createElement("span");
            category.className = "blog-category";
            category.textContent = post.category || "General";

            const title = document.createElement("h3");
            title.textContent = post.title;

            const description = document.createElement("p");
            description.textContent = post.content.slice(0, 130) + "...";

            const meta = document.createElement("div");
            meta.className = "blog-meta";
            meta.textContent =
                `By ${post.author} · ${post.reading_time} min read`;

            const likeButton = document.createElement("button");
            likeButton.className = "like-btn";
            likeButton.textContent = post.is_liked
                ? `❤️ Liked (${post.like_count})`
                : `🤍 Like (${post.like_count})`;

            likeButton.addEventListener("click", async (e) => {
                e.stopPropagation();
                await toggleLike(post.slug, likeButton);
            });

            const bookmarkButton = document.createElement("button");
            bookmarkButton.className = "bookmark-btn";
            bookmarkButton.textContent = post.is_bookmarked
                ? "🔖 Saved"
                : "🔖 Save";

            bookmarkButton.addEventListener("click", async (e) => {
                e.stopPropagation();
                await toggleBookmark(post.slug, bookmarkButton);
            });

            info.append(category, title, description, meta, likeButton, bookmarkButton);
            card.append(image, info);
            container.appendChild(card);
        });

        document.getElementById("loadMoreBtn").style.display =
            nextPage ? "block" : "none";

    } catch (error) {
        console.error(error);
        container.innerHTML = "<p>Could not load blogs.</p>";
    }
}

// SEARCH
function searchBlogs() {
    currentSearch = document.getElementById("searchInput").value;
    const params = new URLSearchParams();

    if (currentSearch) params.append("search", currentSearch);
    if (currentCategory) params.append("category", currentCategory);

    fetchBlogs(API_URL + "?" + params.toString());
}

// CATEGORY FILTER
function filterCategory(category) {
    currentCategory = category;

    document.querySelectorAll(".category-btn").forEach(button => {
        button.classList.remove("active");
    });

    event.target.classList.add("active");
    searchBlogs();
}

// LOAD MORE
function loadMoreBlogs() {
    if (nextPage) fetchBlogs(nextPage, true);
}

// NAVIGATION
function scrollToBlogs() {
    document.getElementById("explore").scrollIntoView({
        behavior: "smooth"
    });
}

// OPEN LOGIN
function showLogin() {
    authMode = "login";

    document.getElementById("authModal").style.display = "flex";
    document.getElementById("authTitle").textContent = "Welcome Back!";
    document.getElementById("authSubtitle").textContent =
        "Login to continue your journey.";

    document.getElementById("nameField").style.display = "none";
    document.getElementById("emailField").style.display = "none";

    document.getElementById("authSubmit").textContent = "Login";

    document.getElementById("authSwitch").innerHTML =
        `Don't have an account? <span onclick="showRegister()">Register</span>`;

    document.getElementById("authMessage").textContent = "";
}

// OPEN REGISTER
function showRegister() {
    authMode = "register";

    document.getElementById("authModal").style.display = "flex";
    document.getElementById("authTitle").textContent = "Join BlogSpace!";
    document.getElementById("authSubtitle").textContent =
        "Create your account and start sharing.";

    document.getElementById("nameField").style.display = "none";
    document.getElementById("emailField").style.display = "block";

    document.getElementById("authSubmit").textContent = "Create Account";

    document.getElementById("authSwitch").innerHTML =
        `Already have an account? <span onclick="showLogin()">Login</span>`;

    document.getElementById("authMessage").textContent = "";
}

// CLOSE MODAL
function closeAuth() {
    document.getElementById("authModal").style.display = "none";
    document.getElementById("authForm").reset();
}

// LOGIN / REGISTER SUBMISSION
document.getElementById("authForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const message = document.getElementById("authMessage");

    const payload = { username, password };

    if (authMode === "register") {
        payload.email = document.getElementById("email").value.trim();

        if (password.length < 8) {
            message.textContent = "Password must contain at least 8 characters.";
            return;
        }
    }

    const endpoint = authMode === "login"
        ? "/api/accounts/login/"
        : "/api/accounts/register/";

    try {
        await setupCSRF();

        const response = await fetch(endpoint, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            message.textContent =
                data.error ||
                Object.values(data).flat().join(" ");
            return;
        }

        message.textContent = "Success! Welcome, " + data.username;

        setTimeout(() => {
            closeAuth();
            checkUser();
        }, 800);

    } catch (error) {
        message.textContent = "Something went wrong. Try again.";
        console.error(error);
    }
});

// CHECK CURRENT USER
async function checkUser() {
    try {
        const response = await fetch("/api/accounts/me/", {
            credentials: "same-origin"
        });

        const loginButton = document.querySelector(".login-btn");
        const signupButton = document.querySelector(".signup-btn");
        const createButton = document.getElementById("createPostBtn");
        if (response.ok) {
            const user = await response.json();
            createButton.style.display = "inline-block";

            loginButton.textContent = user.username;
            loginButton.onclick = null;

            signupButton.textContent = "Logout";
            signupButton.onclick = logoutUser;
        } else {
            createButton.style.display = "none";
            loginButton.textContent = "Login";
            loginButton.onclick = showLogin;

            signupButton.textContent = "Get Started ↗";
            signupButton.onclick = showRegister;
        }

    } catch (error) {
        console.error(error);
    }
}

// LOGOUT
async function logoutUser() {
    try {
        await setupCSRF();

        const response = await fetch("/api/accounts/logout/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        });

        if (response.ok) {
            alert("Logged out successfully!");
            checkUser();
        }

    } catch (error) {
        console.error(error);
    }
}

// INITIALIZE
document.addEventListener("DOMContentLoaded", async () => {
    await setupCSRF();
    fetchBlogs();
    checkUser();

    const params = new URLSearchParams(window.location.search);

    if (params.get("create") === "1") {
        openCreatePost();
    }
});

// OPEN CREATE BLOG
function openCreatePost() {
    document.getElementById("postModal").style.display = "flex";
}

// CLOSE CREATE BLOG
function closeCreatePost() {
    document.getElementById("postModal").style.display = "none";
    document.getElementById("createPostForm").reset();
}

// SUBMIT NEW BLOG
document.getElementById("createPostForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const message = document.getElementById("postMessage");

    const postData = {
        title: document.getElementById("postTitle").value.trim(),
        content: document.getElementById("postContent").value.trim(),
        tags_input: document.getElementById("postTags").value,
        cover_image: document.getElementById("postImage").value.trim(),
        status: document.getElementById("postStatus").value
    };

    try {
        await setupCSRF();

        const response = await fetch("/api/posts/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify(postData)
        });

        const data = await response.json();

        if (!response.ok) {
            message.textContent = JSON.stringify(data);
            return;
        }

        message.textContent = "Blog created successfully! 🎉";

        document.getElementById("createPostForm").reset();

        setTimeout(() => {
            closeCreatePost();
            fetchBlogs();
        }, 1000);

    } catch (error) {
        message.textContent = "Something went wrong!";
        console.error(error);
    }
});

// LIKE / UNLIKE POST
async function toggleLike(slug, button) {

    try {
        await setupCSRF();

        const response = await fetch(`/api/posts/${slug}/like/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        });

        if (response.status === 403 || response.status === 401) {
            alert("Please login to like posts!");
            showLogin();
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            alert("Could not update like.");
            return;
        }

        button.textContent = data.liked
            ? `❤️ Liked (${data.like_count})`
            : `🤍 Like (${data.like_count})`;

    } catch (error) {
        console.error(error);
        alert("Something went wrong!");
    }
}

// BOOKMARK / REMOVE BOOKMARK
async function toggleBookmark(slug, button) {

    try {
        await setupCSRF();

        const response = await fetch(
            `/api/posts/${encodeURIComponent(slug)}/bookmark/`,
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            }
        );

        if (response.status === 401 || response.status === 403) {
            alert("Please login to bookmark posts!");
            showLogin();
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            alert("Could not update bookmark.");
            return;
        }

        button.textContent = data.bookmarked
            ? "🔖 Saved"
            : "🔖 Save";

    } catch (error) {
        console.error(error);
        alert("Something went wrong!");
    }
}