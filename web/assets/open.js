(function () {
  const querylist = Object.entries(queries);
  if (querylist.length > 0) {
    for (const row of document.getElementsByClassName("queryrow")) {
      const keyword = row.querySelector(".querykeyword").textContent;
      for (const [name, f] of querylist) {
        const url = f(keyword);
        const link = document.createElement("a");
        link.textContent = name;
        link.href = url;
        link.target = "_blank";
        row.querySelector(".querylinks").appendChild(link);
      }
    }
  }
})();
