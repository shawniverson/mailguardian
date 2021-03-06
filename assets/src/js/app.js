import Vue from 'vue';
import axios from 'axios';
import components from './components/global_components';
import * as moment from 'moment';
import Nl2br from 'vue-nl2br';
import vSelect from 'vue-select';
import VModal from 'vue-js-modal';
import * as Cookies from "js-cookie";

window.Vue = Vue;
window.moment = moment;
Vue.component('nl2br', Nl2br);
Vue.component('v-select', vSelect);
Vue.use(VModal, { dialog: true, dynamic: true, injectModalsContainer: true });

import {store} from './vuex/store';

import router from './routing/router';

/**
 * We'll load the axios HTTP library which allows us to easily issue requests
 * to our Laravel back-end. This library automatically handles sending the
 * CSRF token as a header based on the value of the "XSRF" token cookie.
 */

window.axios = axios;

window.axios.interceptors.request.use(request => {
    if(process.env.NODE_ENV != "production") {
        console.log('Starting Request', request);
    }
    if (!request.url.includes('github')) {
        request.headers['X-CSRFToken'] = Cookies.get('csrftoken');
        request.headers['X-Requested-With'] = 'XMLHttpRequest';
    }
    return request;
});
window.axios.interceptors.response.use(response => {
    if(process.env.NODE_ENV != "production") {
        console.log('Response for previous request to ' + response.request.responseURL + ': ', response);
    }
    return response;
});

/**
 * Global helper method to perform redirection inside the application
 */
window.redirect = function(url) {
    router.push(url);
}

Vue.filter('yesno', value => {
    return value ? 'Yes' : 'No';
});

Vue.filter('byte_display', value => {
    let kb = 1024;
    let mb = 1024 * 1024;
    let gb = 1024 * 1024 * 1024;
    if (value < kb) {
        return value + ' B';
    }
    else if (value >= kb && value < mb) {
        return (value / kb).toFixed(2) + ' KB';
    }
    else if (value >= mb && value < gb) {
        return (value / mb).toFixed(2) + ' MB';
    }
    else {
        return (value / gb).toFixed(2) + ' GB';
    }
});

Vue.filter('ago', value => {
    return moment(value).fromNow();
})

Vue.mixin({
    methods: {
        createNotification(title, message, type='info', persistent=false) {
            return {
                'title': title,
                'message': message,
                'type': type,
                'persistent': persistent
            };
        }
    }
})

/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

import { mapGetters, mapActions, mapMutations } from 'vuex';

const app = new Vue({
    el: '#app',
    router,
    store,
    components,
    async created() {
        this.setInitializing(true);
        await this.getAppInfo();
        await this.checkSession().then(() => this.getSettings());
        this.setInitializing(false);
    },
    methods: {
        ...mapActions(['checkSession', 'getCurrentUser', 'getSettings', 'getAppInfo']),
        ...mapMutations(['toggleLoading' ,'notify', 'setInitializing'])
    },
    computed: {
        ...mapGetters(['loading', 'isLoggedIn', 'user', 'initializing'])
    }
});