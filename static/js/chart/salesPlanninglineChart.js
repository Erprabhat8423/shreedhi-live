
var linechartvar = document.getElementById("myLineChart").getContext("2d");
var myLineChart = new Chart(linechartvar, {
    type: "line",
    data: {
        datasets: [
            {
            label: 'Bar Dataset',
            data: [19000, 63000, 20000, 74000,20000, 32000, 60000, 25000,20000, 63000, 10000, 44000],
            backgroundColor: "transparent",
            borderColor: 'red',
            borderWidth: 2,
            type: "line",
        }, 
        {
            label: 'Bar Dataset',
            data: [21000, 33000, 22000, 44000,22000, 37000, 56000, 28000,40000, 68000, 20000, 64000],
            backgroundColor: "transparent",
            borderColor: 'yellow',
            borderWidth: 2,
            type: "line",
        }, 
        {
            label: 'Line Dataset',
            data: [20000, 32000, 60000, 25000,19000, 63000, 20000, 74000,45000, 67000, 39000, 84000],
            backgroundColor: "transparent",
            borderColor: 'green',
            borderWidth: 2,
            // Changes this dataset to become a line
            type: 'line'
        }],
        labels: ['Apr' ,'May', 'Jun' ,'Jul','Aug','Sep','Oct','Nov','Dec','Jan', 'Feb', 'Mar']
    },
 
    options: {
        // maintainAspectRatio: false,
        responsive:false,
        title: {
            display: true,
            text: 'Custom Dougnt Title',
            fontSize: 18,
            fontColor: '#cc65fe',
        },
      
        tooltips: {
            enabled: true,
            display: true,
            backgroundColor: "#ccc",
            fontColor: '#000',
            titleFontSize: 20,
            tittleFontColor: "green",
            titleSpacing: 3,
            bodyFontSize: 20,
            bodyFontColor: "block",
            bodySpacing: 3,
        },

        legend: {
            display: true,
            position: "bottom",
            align: "end",
            fontColor: "green",
            // lable: {
            //     fontSize: 30,
            //     fontColor: "green",
            //     boxWidth: 50,                
            // },
        },
        animation: {
            duration: 2000,
            easing: "easeInOutBounce",

        },
        // events: ["click"],
        onClick: function(){
            console.log(" On Click kk");
        },
        onHover: function(){
            console.log(" On Hover kk");
        },
        layout: {
            padding: {
                left: 50,
                right: 0,
                top: 0,
                bottom: 0
            }
        }
    }
});

