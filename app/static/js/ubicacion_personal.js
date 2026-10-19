const colombiaDataUrl = new URL(
  "../data/colombia.json",
  document.currentScript.src
);

document.addEventListener("DOMContentLoaded", async () => {
  const departmentSelect = document.querySelector(
    'select[name="departamento"]'
  );
  const municipalitySelect = document.querySelector(
    'select[name="municipio"]'
  );
  const form = document.getElementById("form-wizard");

  if (!departmentSelect || !municipalitySelect || !form) {
    return;
  }

  const hint = document.createElement("span");
  hint.className = "form-error";
  hint.setAttribute("role", "alert");
  hint.hidden = true;
  municipalitySelect.insertAdjacentElement("afterend", hint);

  const setError = (message) => {
    hint.textContent = message;
    hint.hidden = !message;
  };

  try {
    const response = await fetch(colombiaDataUrl);
    if (!response.ok) {
      throw new Error(`No se pudo cargar DIVIPOLA: HTTP ${response.status}`);
    }

    const catalog = await response.json();
    if (
      !catalog ||
      typeof catalog !== "object" ||
      Object.values(catalog).some(
        (municipalities) =>
          !Array.isArray(municipalities) ||
          municipalities.some((municipality) => typeof municipality !== "string")
      )
    ) {
      throw new Error("El catálogo DIVIPOLA tiene un formato inválido.");
    }

    const updateMunicipalities = (selectedMunicipality = "") => {
      const municipalities = catalog[departmentSelect.value] || [];
      municipalitySelect.replaceChildren(new Option("Seleccione", ""));

      for (const municipality of municipalities) {
        municipalitySelect.add(new Option(municipality, municipality));
      }

      municipalitySelect.value = municipalities.includes(selectedMunicipality)
        ? selectedMunicipality
        : "";
      municipalitySelect.disabled = !departmentSelect.value;
    };

    const savedMunicipality = municipalitySelect.value;
    updateMunicipalities(savedMunicipality);
    departmentSelect.addEventListener("change", () => {
      updateMunicipalities();
      setError("");
    });

    form.addEventListener("submit", (event) => {
      if (
        municipalitySelect.value &&
        !catalog[departmentSelect.value]?.includes(municipalitySelect.value)
      ) {
        event.preventDefault();
        setError("Elige un municipio que pertenezca al departamento seleccionado.");
      }
    });
  } catch (error) {
    console.error(error);
    setError("No se pudo cargar la lista de municipios. Recarga la página e inténtalo de nuevo.");
    departmentSelect.disabled = true;
    municipalitySelect.disabled = true;
    form.addEventListener("submit", (event) => event.preventDefault());
  }
});
