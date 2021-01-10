new Vue({
    el: '#redactForm',
    data: {
        selected : '',
        keys: [],
        date : '',
    },

    methods: {
        getUserKeys(user_id){
            const vm = this;
            axios.get(`/get_users_key_table/?user=${user_id}`).then(function(response){
             vm.keys = response.data})
        },

        formatDate(){
            if (this.selected.date !==undefined){
                let date=this.selected.date;
                date=new Date(date.split('-').join('.')).toISOString().split('T')[0];
                this.date = date;
            }
        }
    },

    created(){
        let uri = window.location.search.substring(1);
        let params = new URLSearchParams(uri);
        let user_id = params.get("user");
        this.getUserKeys(user_id);
        },
});