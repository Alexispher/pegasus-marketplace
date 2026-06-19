const CATEGORIES = ["mods", "plugins", "themes"];

function createFallback(name) {
    const fallback = document.createElement("div");
    fallback.className = "fallback";
    fallback.textContent = name.charAt(0).toUpperCase();
    return fallback;
}

function createCard(item) {
    const card = document.createElement("div");
    card.className = "card";

    if (item.cover) {
        const image = document.createElement("img");
        image.className = "cover";
        image.src = item.cover;
        image.alt = item.name;
        card.appendChild(image);
    } else {
        card.appendChild(createFallback(item.name));
    }

    const category = document.createElement("div");
    category.className = "category";
    category.textContent = item.category.toUpperCase();
    card.appendChild(category);

    const title = document.createElement("div");
    title.className = "title";
    title.textContent = item.name.toUpperCase();
    card.appendChild(title);

    if (item.description) {
        const description = document.createElement("div");
        description.className = "description";
        description.textContent = item.description;
        card.appendChild(description);
    }

    if (item.version) {
        const version = document.createElement("div");
        version.className = "version";
        version.textContent = `v${item.version}`;
        card.appendChild(version);
    }

    if (item.author) {
        const author = document.createElement("div");
        author.className = "author";
        author.textContent = `by ${item.author}`;
        card.appendChild(author);
    }

    return card;
}

async function loadContent() {
    const market = document.getElementById("market");
    market.innerHTML = "";

    try {
        const response = await fetch("index.json");

        if (!response.ok) {
            throw new Error("index.json not found");
        }

        const data = await response.json();

        CATEGORIES.forEach(category => {
            if (!Array.isArray(data[category])) return;

            data[category].forEach(item => {
                const card = createCard(item);
                market.appendChild(card);
            });
        });
    } catch (error) {
        console.error("Failed to load marketplace index:", error);

        const message = document.createElement("div");
        message.className = "card";
        message.textContent = "MARKETPLACE INDEX NOT FOUND";
        market.appendChild(message);
    }
}

loadContent();
