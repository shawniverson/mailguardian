import Vue from 'vue';
import VueRouter from 'vue-router';
import routes from './routes';
import {store} from '../vuex/store';
Vue.use(VueRouter);
const router = new VueRouter({
    routes,
    mode: 'history'
});
router.beforeEach(async (to, from, next) => {
    store.commit('setLoading', true);
    console.log('router before each is called');
    let result = {};
    let allowed = [
        '/password-reset',
        '/setup'
    ];
    window.axios.post('/api/installed/').then(response => {
        if (response.status == 204) {
            if (to.path != '/setup') {
                next({ path: '/setup' });
            }
        }
        else if(response.status == 200) {
            window.mailguardian = response.data;
            if (to.path == '/setup') {
                next({ path: '/' });
            }
        }
        else {
            next();
        }
        return;
    })
    if (!allowed.some(w => to.path.startsWith(w))) {
        window.axios.post('/api/current-user/').then(response => {
            if (to.matched.some(record => record.meta.requiresAuth)) {
                if (response.status == 403 && to.path != '/login') {
                    next({
                        path: '/login?next=' + to.path
                    });
                }
                else {
                    next();
                }
            }
            else if(to.matched.some(record => record.meta.requiresDomainAdmin)) {
                if (response.status == 403 && !response.data.user.is_domain_admin) {
                    next({ path: '/403', replace:false });
                }
                else {
                    next();
                }
            }
            else if(to.matched.some(record => record.meta.requiresAdmin)) {
                if (response.status == 403 && !response.data.user.is_staff) {
                    next({ path: '/403', replace:false });
                }
                else {
                    next();
                }
            }
            else {
                next();
            }
        }).catch(error => {
            if (error.response.status == 403 && to.path != '/login') {
                next({
                    path: '/login?next=' + to.path
                });
            }
            else {
                next();
            }
        })
    }
    else {
        
        next();
    }
    
});
export default router;