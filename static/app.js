new Vue({
    el: '#orders_app',
    data: {
        orders: []
    },
    created: function(){
        const vm = this;
        axios.get('/keys/')
        .then(function(response){
         vm.orders = response.data
        })
    }
});
