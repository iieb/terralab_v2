document.addEventListener('DOMContentLoaded', function () {

    // ----------------------------------------------------------------
    // URLs
    // ----------------------------------------------------------------
    const urlContainer = document.getElementById('url-container');
    if (!urlContainer) return;

    const urlComponentes       = urlContainer.dataset.urlComponentes;
    const urlEquipes           = urlContainer.dataset.urlEquipes;
    const urlEquipesAdicionais = urlContainer.dataset.urlEquipesAdicionais;
    const urlAtividades        = urlContainer.dataset.urlAtividades;
    const urlIndicadores       = urlContainer.dataset.urlIndicadores;
    const urlSubatividades     = urlContainer.dataset.urlSubatividades;

    // ----------------------------------------------------------------
    // Stepper
    // ----------------------------------------------------------------
    let currentStep = 1;
    const totalSteps = 3;

    function goToStep(step) {
        document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
        document.getElementById(`step-${step}`).classList.add('active');

        document.querySelectorAll('.step').forEach(el => {
            const s = parseInt(el.dataset.step);
            el.classList.remove('active', 'completed');
            if (s === step) el.classList.add('active');
            if (s < step)  el.classList.add('completed');
        });

        document.querySelectorAll('.step-line').forEach((line, idx) => {
            line.classList.toggle('completed', idx < step - 1);
        });

        currentStep = step;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    document.getElementById('btn-to-step2').addEventListener('click', () => {
        if (validateStep(1)) goToStep(2);
    });
    document.getElementById('btn-to-step3').addEventListener('click', () => {
        if (validateStep(2)) goToStep(3);
    });
    document.getElementById('btn-back-to-step1').addEventListener('click', () => goToStep(1));
    document.getElementById('btn-back-to-step2').addEventListener('click', () => goToStep(2));

    // ----------------------------------------------------------------
    // Validação por etapa
    // ----------------------------------------------------------------
    function validateStep(step) {
        const stepEl = document.getElementById(`step-${step}`);
        const required = stepEl.querySelectorAll('[required]');
        let valid = true;
        required.forEach(field => {
            if (!field.value.trim()) {
                markInvalid(field);
                valid = false;
            } else {
                markValid(field);
            }
        });
        if (!valid) {
            const first = stepEl.querySelector('.invalid');
            if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return valid;
    }

    function markValid(el)   { el.classList.add('valid');   el.classList.remove('invalid'); }
    function markInvalid(el) { el.classList.add('invalid'); el.classList.remove('valid');   }

    // ----------------------------------------------------------------
    // Cascata: Projeto → Componente + Equipe
    // ----------------------------------------------------------------
    document.getElementById('id_projeto').addEventListener('change', function () {
        const projetoId = this.value;

        const compSelect  = document.getElementById('id_componente');
        const ativSelect  = document.getElementById('id_atividade');
        const equipeSelect = document.getElementById('id_equipe_projeto');

        resetSelect(compSelect,   'Selecione um componente', true);
        resetSelect(ativSelect,   'Selecione uma atividade', true);
        resetSelect(equipeSelect, 'Selecione', true);
        document.getElementById('indicadores').innerHTML = '';
        resetSelect(document.getElementById('id_subatividade'), 'Selecione uma subatividade');
        document.getElementById('subatividade-group').style.display = 'none';

        if (!projetoId) return;

        fetch(`${urlComponentes}?projeto=${projetoId}`)
            .then(r => r.json())
            .then(data => {
                data.sort((a, b) => a.nome.localeCompare(b.nome));
                populateSelect(compSelect, data);
                compSelect.disabled = false;
            });

        fetch(`${urlEquipes}?projeto=${projetoId}`)
            .then(r => r.json())
            .then(data => {
                data.sort((a, b) => a.nome.localeCompare(b.nome));
                populateSelect(equipeSelect, data);
                equipeSelect.disabled = false;
            });

        fetch(`${urlEquipesAdicionais}?projeto=${projetoId}`)
            .then(r => r.json())
            .then(data => {
                const container = document.getElementById('id_equipe_adicional');
                container.innerHTML = '';
                data.sort((a, b) => (a.equipe__nome || '').localeCompare(b.equipe__nome || ''));
                data.forEach(item => {
                    const label = document.createElement('label');
                    label.innerHTML = `<input type="checkbox" name="equipe_adicional" value="${item.id}"> ${item.equipe__nome || item.nome || item.id}`;
                    container.appendChild(label);
                });
            });
    });

    // ----------------------------------------------------------------
    // Cascata: Componente → Atividade
    // ----------------------------------------------------------------
    document.getElementById('id_componente').addEventListener('change', function () {
        const compId = this.value;
        const ativSelect = document.getElementById('id_atividade');
        resetSelect(ativSelect, 'Selecione uma atividade', true);
        document.getElementById('indicadores').innerHTML = '';
        resetSelect(document.getElementById('id_subatividade'), 'Selecione uma subatividade');
        document.getElementById('subatividade-group').style.display = 'none';

        if (!compId) return;

        fetch(`${urlAtividades}?componente=${compId}`)
            .then(r => r.json())
            .then(data => {
                data.sort((a, b) => a.nome.localeCompare(b.nome));
                populateSelect(ativSelect, data);
                ativSelect.disabled = false;
            });
    });

    // ----------------------------------------------------------------
    // Cascata: Atividade → Subatividades + Indicadores
    // ----------------------------------------------------------------
    document.getElementById('id_atividade').addEventListener('change', function () {
        const atividadeId = this.value;

        // — Subatividades —
        const subatividadeGroup = document.getElementById('subatividade-group');
        const subatividadeSelect = document.getElementById('id_subatividade');
        resetSelect(subatividadeSelect, 'Selecione uma subatividade');
        subatividadeGroup.style.display = 'none';

        // — Indicadores —
        const container = document.getElementById('indicadores');
        const hint = document.getElementById('indicadores-hint');
        container.innerHTML = '';

        if (!atividadeId) return;

        fetch(`${urlSubatividades}?atividade=${atividadeId}`)
            .then(r => r.json())
            .then(data => {
                if (data.length > 0) {
                    populateSelect(subatividadeSelect, data);
                    subatividadeGroup.style.display = '';
                }
            })
            .catch(err => console.error('Erro ao carregar subatividades:', err));

        fetch(`${urlIndicadores}?atividade=${atividadeId}`)
            .then(r => r.json())
            .then(data => {
                if (data.length === 0) {
                    hint.textContent = 'Nenhum indicador cadastrado para esta atividade.';
                    hint.style.display = 'block';
                    return;
                }
                hint.style.display = 'none';

                data.forEach(item => {
                    const config = indicadoresConfig[item.tipo];
                    if (!config) {
                        console.warn(`Tipo de indicador sem configuração: "${item.tipo}"`);
                        return;
                    }
                    container.appendChild(renderIndicador(item, config));
                });
            })
            .catch(err => console.error('Erro ao carregar indicadores:', err));
    });

    // ----------------------------------------------------------------
    // Render de indicador
    // ----------------------------------------------------------------
    function renderIndicador(item, config) {
        const card = document.createElement('div');
        card.className = 'indicator-card';

        const header = document.createElement('div');
        header.className = 'indicator-card-header';
        header.innerHTML = `<h3>${item.nome}</h3>`;
        card.appendChild(header);

        const body = document.createElement('div');
        body.className = 'indicator-card-body';

        const numericFields = config.filter(f => f.type === 'number');
        const otherFields   = config.filter(f => f.type !== 'number');

        // Campos numéricos em grid
        if (numericFields.length > 0) {
            const grid = document.createElement('div');
            grid.className = 'numeric-grid';
            numericFields.forEach(field => {
                grid.appendChild(renderField(field, `indicadores_${item.id}_${field.name}`));
            });
            body.appendChild(grid);
        }

        // Demais campos
        otherFields.forEach(field => {
            body.appendChild(renderField(field, `indicadores_${item.id}_${field.name}`));
        });

        card.appendChild(body);
        return card;
    }

    function renderField(field, fieldName) {
        const wrapper = document.createElement('div');
        wrapper.className = 'field-group';

        const label = document.createElement('label');
        label.textContent = field.label;
        wrapper.appendChild(label);

        if (field.type === 'number' || field.type === 'text') {
            const input = document.createElement('input');
            input.type = field.type;
            input.name = fieldName;
            input.placeholder = field.label;
            if (field.step) input.step = field.step;
            wrapper.appendChild(input);

        } else if (field.type === 'select') {
            field.options.forEach(option => {
                const div = document.createElement('div');
                div.className = 'radio-option';
                div.innerHTML = `
                    <input type="radio" id="${fieldName}_${option.value}"
                           name="${fieldName}" value="${option.value}">
                    <label for="${fieldName}_${option.value}">${option.label}</label>
                `;
                wrapper.appendChild(div);
            });

        } else if (field.type === 'checkbox') {
            field.options.forEach(option => {
                const div = document.createElement('div');
                div.className = 'checkbox-option';
                div.innerHTML = `
                    <input type="checkbox" id="${fieldName}_${option.value}"
                           name="${fieldName}" value="${option.value}">
                    <label for="${fieldName}_${option.value}">${option.label}</label>
                `;
                wrapper.appendChild(div);
            });
        }

        return wrapper;
    }

    // ----------------------------------------------------------------
    // Collapsible (campos narrativos)
    // ----------------------------------------------------------------
    document.querySelectorAll('.collapsible-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('open');
            const content = btn.nextElementSibling;
            content.classList.toggle('open');
        });
    });

    // ----------------------------------------------------------------
    // Validação no submit
    // ----------------------------------------------------------------
    document.getElementById('main-form').addEventListener('submit', function (e) {
        let valid = true;
        for (let s = 1; s <= totalSteps; s++) {
            if (!validateStep(s)) {
                valid = false;
                if (currentStep !== s) goToStep(s);
                break;
            }
        }
        if (!valid) {
            e.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios.');
        }
    });

    // ----------------------------------------------------------------
    // Helpers
    // ----------------------------------------------------------------
    function resetSelect(select, placeholder, disable = false) {
        select.innerHTML = `<option value="">${placeholder}</option>`;
        select.disabled = disable;
    }

    function populateSelect(select, data) {
        data.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.nome;
            select.appendChild(opt);
        });
    }

    // Validação em tempo real nos campos obrigatórios da etapa 1
    document.querySelectorAll('#step-1 [required]').forEach(field => {
        field.addEventListener('change', () => field.value.trim() ? markValid(field) : markInvalid(field));
    });

    // ----------------------------------------------------------------
    // Feedback visual nos campos de upload de arquivo
    // ----------------------------------------------------------------
    document.querySelectorAll('.file-upload-area input[type="file"]').forEach(input => {
        input.addEventListener('change', function () {
            const label = this.closest('.file-upload-area').querySelector('.file-label');
            if (this.files && this.files.length > 0) {
                label.textContent = this.files.length === 1
                    ? this.files[0].name
                    : `${this.files.length} arquivos selecionados`;
                label.style.color = '#d26b16';
            } else {
                label.textContent = label.dataset.default;
                label.style.color = '';
            }
        });
        // Guarda o texto original para restaurar se necessário
        const label = input.closest('.file-upload-area').querySelector('.file-label');
        if (label) label.dataset.default = label.textContent;
    });

});
