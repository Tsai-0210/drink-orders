(function () {
  const drinkSelect = document.querySelector("#drinkSelect");
  const otherDrinkField = document.querySelector("#otherDrinkField");
  const otherDrinkInput = otherDrinkField ? otherDrinkField.querySelector("input") : null;

  function syncOtherDrink() {
    if (!drinkSelect || !otherDrinkField || !otherDrinkInput) return;
    const needsOther = drinkSelect.value === "其他";
    otherDrinkField.classList.toggle("hidden", !needsOther);
    otherDrinkInput.required = needsOther;
    if (!needsOther) otherDrinkInput.value = "";
  }

  if (drinkSelect) {
    drinkSelect.addEventListener("change", syncOtherDrink);
    syncOtherDrink();
  }

  const copyButton = document.querySelector("#copyButton");
  const copyText = document.querySelector("#copyText");

  if (copyButton && copyText) {
    copyButton.addEventListener("click", async function () {
      copyText.select();
      copyText.setSelectionRange(0, copyText.value.length);

      try {
        await navigator.clipboard.writeText(copyText.value);
      } catch (_error) {
        document.execCommand("copy");
      }

      copyButton.textContent = "已複製";
      setTimeout(function () {
        copyButton.textContent = "一鍵複製文字";
      }, 1500);
    });
  }
})();
