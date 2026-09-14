const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".main-nav");
const heroBg = document.querySelector(".hero-bg");
const API_BASE_URL =
  window.MOOVE_API_BASE_URL || (window.location.protocol === "file:" ? "http://127.0.0.1:8002/api" : "/api");
const publicRelatoText = document.querySelector("[data-public-relato-text]");
const publicRelatoAuthor = document.querySelector("[data-public-relato-author]");
const supportForm = document.querySelector(".support-form");
const messageField = document.querySelector(".message-field textarea");
const charCount = document.querySelector(".char-count");
const participationInputs = [...document.querySelectorAll('input[name="participacao"]')];
const supportContactField = document.querySelector(".support-contact-field");
const pilotContactField = document.querySelector(".pilot-contact-field");
const ambassadorContactField = document.querySelector(".ambassador-contact-field");
const supportContactInput = document.querySelector('input[name="contato_apoio"]');
const pilotContactInput = document.querySelector('input[name="contato_piloto"]');
const ambassadorContactInput = document.querySelector('input[name="contato_embaixador"]');
const formStatus = document.querySelector(".form-status");
const revealGroups = [
  [document.querySelector(".problem-stats"), document.querySelector(".problem-quote")],
  [document.querySelector(".wants-list")],
  [...document.querySelectorAll(".solution-cards article")],
  [...document.querySelectorAll(".participate-cards article")],
  [document.querySelector(".support-form")],
];
const animatedCards = revealGroups.flat().filter(Boolean);
let publicRelatoIndex = 0;

toggle?.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("open");
  toggle.setAttribute("aria-expanded", String(isOpen));
});

document.querySelectorAll(".main-nav a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle?.setAttribute("aria-expanded", "false");
  });
});

window.addEventListener(
  "scroll",
  () => {
    const offset = Math.min(window.scrollY * 0.04, 12);
    heroBg.style.transform = `scale(1.012) translateY(${offset}px)`;
  },
  { passive: true }
);

const getSelectedParticipation = () =>
  participationInputs.filter((input) => input.checked).map((input) => input.value);

const setFieldVisibility = (field, input, isVisible) => {
  field?.classList.toggle("is-hidden", !isVisible);
  if (input) {
    input.required = isVisible;
    if (!isVisible) {
      input.value = "";
      input.setCustomValidity("");
    }
  }
};

const syncConditionalFields = () => {
  const selected = getSelectedParticipation();
  setFieldVisibility(supportContactField, supportContactInput, selected.includes("apoiar"));
  setFieldVisibility(pilotContactField, pilotContactInput, selected.includes("piloto"));
  setFieldVisibility(
    ambassadorContactField,
    ambassadorContactInput,
    selected.includes("embaixador")
  );
};

const setFormStatus = (message, type = "neutral") => {
  if (!formStatus) return;
  formStatus.textContent = message;
  formStatus.dataset.type = type;
};

const setPublicRelato = (relato) => {
  if (!publicRelatoText || !publicRelatoAuthor) return;

  publicRelatoText.textContent = `“${relato.mensagem}”`;
  publicRelatoAuthor.textContent = `— Estudante, ${relato.bairro}`;
};

const loadPublicRelatos = async () => {
  if (!publicRelatoText || !publicRelatoAuthor) return;

  try {
    const response = await fetch(`${API_BASE_URL}/relatos?limit=8`);
    if (!response.ok) return;

    const relatos = await response.json();
    if (!Array.isArray(relatos) || relatos.length === 0) return;

    setPublicRelato(relatos[0]);

    if (relatos.length > 1) {
      window.setInterval(() => {
        publicRelatoIndex = (publicRelatoIndex + 1) % relatos.length;
        setPublicRelato(relatos[publicRelatoIndex]);
      }, 7000);
    }
  } catch (error) {
    console.warn("Nao foi possivel carregar relatos publicos.", error);
  }
};

const buildSupportPayload = () => {
  const formData = new FormData(supportForm);

  return {
    nome: formData.get("nome"),
    instituicao: formData.get("instituicao"),
    bairro: formData.get("bairro"),
    turno: formData.get("turno"),
    faixa_etaria: formData.get("faixa_etaria"),
    participacao: getSelectedParticipation(),
    contato_apoio: formData.get("contato_apoio") || null,
    contato_piloto: formData.get("contato_piloto") || null,
    contato_embaixador: formData.get("contato_embaixador") || null,
    mensagem: formData.get("mensagem") || null,
    confirmou_piloto: formData.get("confirmo") === "on",
    confirmou_independencia: formData.get("independente") === "on",
  };
};

const getApiErrorMessage = async (response) => {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => item.msg || item.message)
        .filter(Boolean)
        .join(" ");
    }
    if (typeof data.detail === "string") return data.detail;
    if (typeof data.message === "string") return data.message;
  } catch (error) {
    return null;
  }

  return null;
};

participationInputs.forEach((input) => {
  input.addEventListener("change", () => {
    participationInputs.forEach((item) => item.setCustomValidity(""));
    syncConditionalFields();
    setFormStatus("");
  });
});

syncConditionalFields();
loadPublicRelatos();

supportForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (getSelectedParticipation().length === 0) {
    participationInputs[0]?.setCustomValidity("Selecione pelo menos uma forma de participação.");
    participationInputs[0]?.reportValidity();
    setFormStatus("Selecione pelo menos uma forma de participação.", "error");
    return;
  }

  participationInputs.forEach((input) => input.setCustomValidity(""));
  syncConditionalFields();

  if (!supportForm.reportValidity()) {
    setFormStatus("Confira os campos obrigatórios antes de enviar.", "error");
    return;
  }

  const button = supportForm.querySelector(".submit-support");
  const originalContent = button.innerHTML;
  button.disabled = true;
  button.textContent = "Enviando...";
  setFormStatus("Enviando seu apoio...", "neutral");

  try {
    const response = await fetch(`${API_BASE_URL}/apoios`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(buildSupportPayload()),
    });

    if (!response.ok) {
      const apiMessage = await getApiErrorMessage(response);
      throw new Error(apiMessage || "Não foi possível registrar seu apoio.");
    }

    button.textContent = "Apoio registrado";
    setFormStatus("Apoio registrado com sucesso.", "success");
    supportForm.reset();
    syncConditionalFields();
    window.setTimeout(() => {
      button.innerHTML = originalContent;
      button.disabled = false;
    }, 1800);
    if (charCount && messageField) {
      charCount.textContent = `0 / ${messageField.maxLength}`;
    }
  } catch (error) {
    button.innerHTML = originalContent;
    button.disabled = false;
    setFormStatus(error.message || "Erro ao registrar apoio. Tente novamente.", "error");
  }
});

messageField?.addEventListener("input", () => {
  if (charCount) {
    charCount.textContent = `${messageField.value.length} / ${messageField.maxLength}`;
  }
});

revealGroups.forEach((group) => {
  group.filter(Boolean).forEach((card, index) => {
    card.classList.add("reveal-card");
    card.style.setProperty("--reveal-delay", `${index * 80}ms`);
  });
});

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.18, rootMargin: "0px 0px -8% 0px" }
  );

  animatedCards.forEach((card) => revealObserver.observe(card));
} else {
  animatedCards.forEach((card) => card.classList.add("is-visible"));
}
