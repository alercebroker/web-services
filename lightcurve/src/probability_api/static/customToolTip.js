export function customToolTip(context) {
    let tooltipEl = document.getElementById('chartjs-tooltip');

    if(!tooltipEl){
        tooltipEl = document.createElement('div')
        tooltipEl.id = 'chartjs-tooltip';
        tooltipEl.innerHTML = '<table></table>';
        document.body.appendChild(tooltipEl);
    }

    let tooltipModel = context.tooltip;
    
    if(tooltipModel.opacity === 0){
        tooltipEl.style.opacity = 0;
        return;
    }

    tooltipEl.classList.remove('above', 'below', 'no-transform');
    if(tooltipModel.yAlign){
        tooltipEl.classList.add(tooltipModel.yAlign);
    } else {
        tooltipEl.classList.add('no-transform')
    }

    function getBody(bodyItem) {
        return bodyItem.lines;
    }

    // set Text
    if(tooltipModel.body){
        let titleLines = tooltipModel.title || [];
        let bodyLines = tooltipModel.body.map(getBody);

        let innerHtml = '<thead>';

        titleLines.forEach(function(title) {
            innerHtml += '<tr><th style="color: #fff; width: 140px; height: 12px;padding: 4px;">' + title + ' (score)' + '</th></tr>';
        });

        innerHtml += '</thead><tbody>';

        /** invertir objecto */
        innerHtml += '<tr><td style="color: #fff; height: 12px; max-width: 100%;">' + bodyLines[0][0] + '</td></tr>'
        
        let style = ""
        for (let index = bodyLines.length - 1; index >= 1; index--){
            style = ' color: #fff;';
            style = style + ' max-width: 100%;';
            style = style + ' height: 12px;';
            innerHtml += '<tr><td style="' + style + '">' + bodyLines[index][0] + '</td></tr>';
        }

        innerHtml += '</tbody>';

        let tableRoot = tooltipEl.querySelector('table');
        tableRoot.innerHTML = innerHtml;
    }

    let position = context.chart.canvas.getBoundingClientRect();
    let bodyFont = Chart.helpers.toFont(tooltipModel.options.bodyFont);

    // Display, position, and set styles for font
    tooltipEl.style.opacity = 1;
    tooltipEl.style.backgroundColor = 'rgba(50, 50, 50, 0.7)'
    tooltipEl.style.position = 'absolute';
    tooltipEl.style.left = position.left + window.scrollX + tooltipModel.caretX + 'px';
    tooltipEl.style.bottom = (window.innerHeight - (position.top + window.scrollY + tooltipModel.caretY)) + 'px';
    tooltipEl.style.font = bodyFont.string;
    tooltipEl.style.pointerEvents = 'none';
}