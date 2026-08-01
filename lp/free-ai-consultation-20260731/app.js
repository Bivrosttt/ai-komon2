(function () {
  "use strict";

  var key = document.body.dataset.industry;
  var data = window.FREE_CONSULT_LP_DATA && window.FREE_CONSULT_LP_DATA[key];
  if (!data) return;

  var requestedLayout = new URLSearchParams(window.location.search).get("layout");
  // All industry LPs share the approved editorial first view by default.
  // The poster remains available explicitly via ?layout=poster.
  var layout = requestedLayout === "poster" ? "poster" : "editorial";
  if (layout === "editorial" || layout === "poster") {
    document.body.classList.add("layout-" + layout);
  }

  function set(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  document.title = "AI顧問室｜" + data.label + "向け AI活用コンサル1回分無料";
  document.querySelector('meta[name="description"]').setAttribute("content", data.label + "の業務を伺い、AIを使えるところと最初に見直す業務を整理するコンサル1回分を無料で提供しています。");
  set("hero-title", data.title);
  set("hero-lead", data.lead);
  set("hero-example", data.example);
  set("quote", data.quote);
  set("scene-title", data.sceneTitle);
  set("scene-body", data.sceneBody);

  var bridge = document.querySelector(".bridge");
  var bridgeCopy = bridge && bridge.querySelector(".bridge-grid > div:first-child");
  var quote = document.getElementById("quote");
  if (bridge && bridgeCopy && quote && Array.isArray(data.possibleTasks)) {
    var bridgeTitle = bridge.querySelector(".section-title");
    var bridgeLead = bridge.querySelector(".section-lead");
    if (bridgeTitle) bridgeTitle.textContent = "例えば、こんな業務を効率化できます。";
    if (bridgeLead) bridgeLead.textContent = "業務の流れを伺ったうえで、AIを使える可能性のある箇所を整理します。";

    var taskLabel = document.createElement("p");
    taskLabel.className = "bridge-task-label";
    taskLabel.textContent = "AIで効率化できる可能性のある業務";

    var taskList = document.createElement("ul");
    taskList.className = "possible-tasks";
    taskList.id = "possible-tasks";
    data.possibleTasks.forEach(function (task) {
      var item = document.createElement("li");
      item.textContent = task;
      taskList.appendChild(item);
    });

    var exampleLabel = document.createElement("p");
    exampleLabel.className = "bridge-example-label";
    exampleLabel.textContent = data.label + "業での一例";

    bridgeCopy.insertBefore(taskLabel, quote);
    bridgeCopy.insertBefore(taskList, quote);
    bridgeCopy.insertBefore(exampleLabel, quote);
  }

  set("first-step", data.firstStep);
  set("final-title", data.label + "の業務を、まず聞かせてください。");
  set("final-lead", "AIで何ができるか決まっていなくても大丈夫です。コンサル1回分で、いまの業務と最初に見直すところを一緒に整理します。");

  if (layout === "editorial" || layout === "poster") {
    var heroCopy = document.querySelector(".hero-copy");
    var heroTitle = document.getElementById("hero-title");
    var heroLead = document.getElementById("hero-lead");

    if (heroCopy && !heroCopy.querySelector(".hero-brand")) {
      var heroBrand = document.createElement("div");
      var brandName = document.createElement("strong");
      var brandDivider = document.createElement("span");
      var brandDescription = document.createElement("small");

      heroBrand.className = "hero-brand";
      brandName.textContent = "AI顧問室";
      brandDivider.className = "hero-brand-divider";
      brandDivider.setAttribute("aria-hidden", "true");
      brandDescription.textContent = "業務改善のためのAIコンサル";
      heroBrand.append(brandName, brandDivider, brandDescription);
      heroCopy.insertBefore(heroBrand, heroCopy.firstChild);
    }

    function setLines(element, lines) {
      if (!element) return;
      element.replaceChildren();
      lines.forEach(function (line, index) {
        element.append(document.createTextNode(line));
        if (index < lines.length - 1) element.append(document.createElement("br"));
      });
    }

    setLines(heroLead, [
      "仕事の流れを伺い、AIを使える場所と、",
      "最初に見直す業務を整理します。"
    ]);

    if (layout === "editorial") {
      setLines(heroTitle, [
        "AIを使いたい。",
        "まずは、いまの業務を",
        "聞かせてください。"
      ]);
    } else {
      setLines(heroTitle, [
        "AIを使いたい。",
        "まずは、いまの",
        "業務を",
        "聞かせてください。"
      ]);
    }
  }

  var industryImage = document.getElementById("industry-image");
  if (industryImage) {
    industryImage.src = data.image;
    industryImage.alt = data.imageAlt;
  }

  var heroImage = document.getElementById("hero-image");
  if (heroImage) {
    var industryHeroImages = {
      kensetsu: "../../output/imagegen/final-ads/kensetsu-bg.png",
      fudosan: "../../output/imagegen/final-ads/fudosan-bg.png",
      seizo: "../../output/imagegen/final-ads/seizo-bg.png",
      unsou: "../../output/imagegen/final-ads/unsou-bg.png",
      shukuhaku: "../../output/imagegen/final-ads/shukuhaku-bg.png"
    };
    var industryHeroImage = industryHeroImages[key];
    heroImage.src = layout === "editorial"
      ? industryHeroImage
      : layout === "poster"
        ? industryHeroImage
        : "../../assets/lp-zukai/hero-consultation-editorial.png";
    heroImage.alt = data.label + "の業務改善を検討している様子";
  }

  // The ad LP is the conversion entry point. Send every CTA straight to the
  // booking calendar instead of making the visitor pass through lp-zukai.
  // measurement.js adds the first-touch UTM values and anonymous session ID
  // on production before the visitor leaves for TimeRex.
  var destination = "https://timerex.net/s/koki.otsuka_bfac/4b686119?from=free_consult_" + key;
  document.querySelectorAll("[data-cta]").forEach(function (link) {
    link.href = destination;
    link.textContent = "コンサル1回分を無料申し込み";
    link.dataset.industry = key;
  });
  if (typeof window.aiKomonDecorateLinks === "function") {
    window.aiKomonDecorateLinks();
  }

  if (layout === "editorial" || layout === "poster") {
    var hero = document.querySelector(".hero");
    if (hero && !document.querySelector(".reference-artboard")) {
      var referenceArtboard = document.createElement("a");
      var referenceImage = document.createElement("img");
      var referenceFile = layout === "editorial"
        ? "ai-komon-fv-proposal-01-editorial-split.png"
        : "ai-komon-fv-proposal-04-terracotta-poster.png";

      referenceArtboard.className = "reference-artboard reference-artboard-" + layout;
      referenceArtboard.href = destination;
      referenceArtboard.dataset.cta = "";
      referenceArtboard.dataset.industry = key;
      referenceArtboard.setAttribute("aria-label", "コンサル1回分を無料申し込み");
      referenceImage.src = "../../output/imagegen/" + referenceFile;
      referenceImage.alt = "";
      referenceImage.width = 1672;
      referenceImage.height = 941;

      referenceArtboard.append(referenceImage);
      hero.parentNode.insertBefore(referenceArtboard, hero);
    }
  }

  if (typeof window.aiKomonGaTrack === "function") {
    window.aiKomonGaTrack("free_consult_lp_view", { industry: key, offer: "first_consultation_free" });
  }
})();
