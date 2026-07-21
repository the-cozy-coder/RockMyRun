


document.getElementById("searchForm")
    .addEventListener("submit", async (e) => {

    e.preventDefault();

    document.getElementById("loadingModal").style.display = "block";

    const formData = new FormData(e.target);

    try {
        const response = await fetch("/search", {
            method: "POST",
            body: formData
        });

        const html = await response.text();

        document.getElementById("results").innerHTML = html;
    }
    catch(err) {
        console.error(err);
    }
    finally {
        document.getElementById("loadingModal").style.display = "none";
    }
});