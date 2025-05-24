"use strict";
const chart = document.getElementById('chartArea');
const shopSelector = document.getElementById('shopSelector');
console.log("main.ts loaded");
shopSelector === null || shopSelector === void 0 ? void 0 : shopSelector.addEventListener('change', () => {
    switchShop(shopSelector.value);
});
function switchShop(shop) {
    console.log("switchShop called with:", shop);
    if (!chart) {
        console.warn("chart element not found");
        return;
    }
    if (shop === "shop1") {
        chart.innerHTML = "📊 Shop 1 - Tel Aviv <br/> [Camera A: 3 cases | Camera B: 1 case | Camera C: 0] (March)";
    }
    else if (shop === "shop2") {
        chart.innerHTML = "📊 Shop 2 - Haifa <br/> [Camera X: 0 | Camera Y: 2 | Camera Z: 4] (March)";
    }
    else if (shop === "shop3") {
        chart.innerHTML = "📊 Shop 3 - Eilat <br/> [Cam 1: 1 case | Cam 2: 1 case | Cam 3: 0] (March)";
    }
}
