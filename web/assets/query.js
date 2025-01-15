(function () {
  const input = document.getElementById("query-input");
  const buttons = document.getElementById("query-buttons");
  const querylist = Object.entries(queries);
  if (querylist.length === 0) {
    buttons.innerHTML = "<p>クエリを持つサイトがありません</p>";
  } else {
    input.addEventListener("input", () => {
      buttons.innerHTML = "";
      const query = input.value.trim();
      if (query) {
        for (const [name, f] of querylist) {
          const url = f(query);
          const button = document.createElement("button");
          button.textContent = name;
          button.onclick = () => {
            window.open(url, "_blank");
          };
          buttons.appendChild(button);
        }
      }
    });
  }
})();
