document.addEventListener('DOMContentLoaded', () => {
    const diseaseGrid = document.getElementById('disease-grid');
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalImage = document.getElementById('modal-image');
    const modalScientificName = document.getElementById('modal-scientific-name');
    const modalCauses = document.getElementById('modal-causes');
    const modalSymptoms = document.getElementById('modal-symptoms');
    const modalSpread = document.getElementById('modal-spread');
    const modalPrevention = document.getElementById('modal-prevention');
    const modalTreatment = document.getElementById('modal-treatment');
    const modalImpact = document.getElementById('modal-impact');
    const modalSeason = document.getElementById('modal-season');

    fetch('/static/data/disease-types.json')
        .then(response => response.json())
        .then(diseases => {
            diseases.forEach(disease => {
                const card = document.createElement('div');
                card.className = 'disease-box';
                card.innerHTML = `
                    <img src="/static/img/${disease.id}.JPG" alt="${disease.name}" class="disease-img">
                    <h3>${disease.name}</h3>
                    <hr class="divider">
                    <p><strong>Causes:</strong> ${disease.causes}</p>
                    <p><strong>Symptoms:</strong> ${disease.symptoms}</p>
                    <a href="javascript:void(0)" class="learn-more" onclick="openModal('${disease.id}')">Learn More</a>
                `;
                diseaseGrid.appendChild(card);
            });
        });

    // Function to open the modal with disease details
    window.openModal = function(id) {
        fetch('/static/data/disease-types.json')
            .then(response => response.json())
            .then(diseases => {
                const disease = diseases.find(d => d.id === id);
                if (disease) {
                    modalTitle.textContent = disease.name;
                    modalScientificName.textContent = disease.scientific_name;
                    modalCauses.textContent = disease.causes;
                    modalSymptoms.textContent = disease.symptoms;
                    modalSpread.textContent = disease.spread_transmission;
                    modalPrevention.textContent = disease.prevention;
                    modalTreatment.textContent = disease.treatment;
                    modalImpact.textContent = disease.impact;
                    modalSeason.textContent = disease.seasonal_occurrence;
                    modal.style.display = 'flex';
                }
            });
    };

    // Function to close the modal
    window.closeModal = function() {
        modal.style.display = 'none';
    };

    // Close the modal when clicking outside the content
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    };
});
