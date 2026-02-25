window.PlotlyConfig = {
  displayModeBar: false,
  responsive: true
};

function getActivityIdFromClickPoint(point) {
  if (!point) return null;
  const customData = point.customdata;
  if (Array.isArray(customData)) {
    return customData.length ? customData[0] : null;
  }
  return customData;
}

function toIntegerActivityId(rawValue) {
  const parsed = Number(rawValue);
  if (!Number.isFinite(parsed)) return null;
  return Math.trunc(parsed);
}

function navigateToActivity(activityId) {
  document.body.classList.add("page-loading");
  window.setTimeout(function () {
    window.location.assign("/activity/" + activityId);
  }, 40);
}

function bindEfficiencyClickNavigation() {
  const plot = document.querySelector("#fig2 .js-plotly-plot");
  if (!plot || plot.dataset.activityClickBound === "1" || typeof plot.on !== "function") return;

  plot.dataset.activityClickBound = "1";
  plot.on("plotly_click", function (eventData) {
    if (!eventData || !Array.isArray(eventData.points)) return;

    for (const point of eventData.points) {
      const rawActivityId = getActivityIdFromClickPoint(point);
      if (rawActivityId === null || rawActivityId === undefined) continue;

      const activityId = toIntegerActivityId(rawActivityId);
      if (activityId === null) continue;

      navigateToActivity(activityId);
      return;
    }
  });
}

window.addEventListener("DOMContentLoaded", function () {
  document.body.classList.add("dash-ready");
  bindEfficiencyClickNavigation();

  const observer = new MutationObserver(function () {
    bindEfficiencyClickNavigation();
  });
  observer.observe(document.body, { childList: true, subtree: true });
});

function shouldHandleActivityNavigation(event, anchor) {
  if (!anchor || event.defaultPrevented) return false;
  if (event.button !== 0) return false;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
  if (anchor.target && anchor.target.toLowerCase() !== "_self") return false;
  if (anchor.hasAttribute("download")) return false;

  const href = anchor.getAttribute("href");
  if (!href || href.startsWith("#") || href.startsWith("javascript:")) return false;

  return true;
}

document.addEventListener("click", function (event) {
  const anchor = event.target.closest("a.activity-list__link");
  if (!shouldHandleActivityNavigation(event, anchor)) return;

  event.preventDefault();
  document.body.classList.add("page-loading");
  window.setTimeout(function () {
    window.location.assign(anchor.href);
  }, 40);
});
