var coords= [];
var coord=[]
var count_coords = {};
count_coords[1] = 0;
count_coords[2] = 0;
count_coords[3] = 0;
var dados_envio=''

console.log(coords)
$(document).ready(function() {
    $("img").on("click", function(event) {
        var x = event.pageX - this.offsetLeft;
        var y = event.pageY - this.offsetTop;
        if (coords.length==3){
    	    //alert("Limite estourado, refresh caso queira recomecar");
    	}
    	else{
    	    coord[0]=x
    	    coord[1]=y
    	    coords[coords.length]= JSON.parse(JSON.stringify(coord));
    	    count_coords[counter]=JSON.stringify(coords)
    	    dados_envio = count_coords[counter]
    	    console.log('dados_envio')
    	    console.log(dados_envio)
    	}
    	console.log(coords.length)
        console.log(coords)
        ////alert("X Coordinate: " + x + " Y Coordinate: " + y);

        return coords
    });


});

    document.addEventListener('click', function(e) {
     e = e || window.event;
     var target = e.target;
     if(target.tagName == 'IMG')
        { console.log(target.src); }
        }, false);

////alert(target.src)

//le arquivo de imagens
var mylist = {{list_json|safe}};

//monta a lista de arquivos
for(i = 0; i < mylist.length; i++){
    mylist[i] = '/static/'+mylist[i];
};

//seleciona o 1o
document.getElementById('imageBox').src = mylist[0]





//desenha boxes
$(document).ready(function(){

    $("img").click(function (ev) {
        if($('div').length < 3) {
            $("body").append(
                $('<div></div>').css({
                    position: 'absolute',
                    top: ev.pageY + 'px',
                    left: ev.pageX + 'px',
                    width: '15px',
                    height: '15px',
                    background: '#000000'
                })
            );
        }
    });

});


//botao envia ondas
$(document).ready(function() {
    $("#send-my-url-to-django-button").click(function() {
        email = document.getElementById('email').value
        if (email=='')
        {
            alert('Coloque seu email')
        } else{
                if (dados_envio !=''){
                    console.log(dados_envio)
                    $.ajax({
                        type: "POST",
                        url: "{% url 'receive_coords' %}",
                        data: {'coords': (dados_envio),'file':imgn,'csrfmiddlewaretoken': '{{ csrf_token }}'},
                        dataType: "json",
                        success: function(response) {
                          if (response['response']=='ok sim'){
                            //alert('dados enviados')
                            dados_envio =''
                            console.log('imagem enviada')
                            console.log(imgn)
                           }
                    }

                    })


                } else{
                    alert("Faltou clicar nas ondas")
                }
        }

    })
})
//botao sem ondas
$(document).ready(function() {
    $("#send-sem-ondas-button").click(function() {
        email = document.getElementById('email').value
        if (email=='')
        {
            alert('Coloque seu email')
        } else{
            dados_envio=''
            imagem = document.getElementById('imageBox').src
            var imagem_str =  JSON.stringify(imagem)
            console.log('imagem..')
            console.log(imagem_str)
            $.ajax({
                type: "POST",
                url: "{% url 'receive_coords' %}",
                data: {'coords': (dados_envio),'file': (imagem_str),'csrfmiddlewaretoken': '{{ csrf_token }}'},
                dataType: "json",
                success: function(response) {
                  change_img()
                  console.log('enviando..')
                  console.log(response)


                }
                  ////alert(response)
            })
        }
    })
})




//seleciona o img da lista de arquivos e define imagem
let counter = 1;
document.querySelector('button').addEventListener('click', function() {
        if (coords.length>0){
            document.getElementById('imageBox').src = mylist[counter];
            $('div').remove();
            if (counter==2){
                counter = 0;
            } else{
                counter++;
            }
            coords= []
            console.log(counter)
        }


    });


function change_img(){
        document.getElementById('imageBox').src = mylist[counter];
        imagem = document.getElementById("imageBox").src;
        $('div').remove();
        if (counter==2){
            counter = 0;
        } else{
            counter++;
        }
        coords= []
    	console.log(counter)
}




document.querySelector('#send-sem-ondas-button').addEventListener('click', function() {
        document.getElementById('imageBox').src = mylist[counter];
        $('div').remove();
    	if (counter==2){
    	    counter = 0;
    	} else{
    	    counter++;
    	}
        coords= []
    	console.log(counter)



    });

