 const AdminDashboard = {
    template: `
        <div>
            <nav class="bg-gray-800 px-4 py-4">
                <ul class="flex space-x-4">
                    <li class="text-white font-bold text-2xl cursor-pointer">IESCP</li>
                    <li class="text-gray-400 hover:text-white cursor-pointer"><router-link to="/dashboard">Dashboard</router-link></li>
                    <li class="text-gray-400 hover:text-white cursor-pointer"><router-link to="/sponsors">Sponsors</router-link></li>
                    <li class="text-gray-400 hover:text-white cursor-pointer"><router-link to="/influencers">Influencers</router-link></li>
                    <li class="text-gray-400 hover:text-white cursor-pointer"><router-link to="/campaigns">Campaigns</router-link></li>
                    <li class="text-gray-400 hover:text-white cursor-pointer"><router-link to="/posts">Influencer's Posts</router-link></li>
                    <button class="rounded-lg px-2 bg-white hover:text-white font-bold hover:font-bold hover:bg-black active:bg-gray-800 ring-5 ring-black outline-none focus:outline-none focus:ring focus:ring-white">
                        <a href="/">Log Out</a>
                    </button>
                </ul>
            </nav>
            <div class="container mx-auto mt-8">
                <router-view></router-view>
            </div>
        </div>
    `
};

const Dashboard = {
    template: `
        <div>
            <h2 class="text-4xl font-bold text-gray-800 mb-4">Admin Dashboard Stats</h2>
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Influencers</h3>
                    <p class="text-2xl text-gray-700">{{ total_influencers }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Sponsors</h3>
                    <p class="text-2xl text-gray-700">{{ total_sponsors }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Campaigns</h3>
                    <p class="text-2xl text-gray-700">{{ total_campaigns }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Campaigns(Public)</h3>
                    <p class="text-2xl text-gray-700">{{ total_active_campaigns }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Campaigns(Private)</h3>
                    <p class="text-2xl text-gray-700">{{ total_inactive_campaigns }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Posts</h3>
                    <p class="text-2xl text-gray-700">{{ total_posts }}</p>
                </div>
                <div class="bg-white p-4 shadow-lg rounded-lg">
                    <h3 class="text-xl font-semibold text-gray-800">Total Ad Requests</h3>
                    <p class="text-2xl text-gray-700">{{ total_adreqeusts }}</p>
                </div>
            </div>
            <h3 class="text-2xl mt-4 font-semibold text-gray-800 mb-4">Charts</h3>
            <div class="mt-8 chart-container">
                
                
                <div>
                    <h3>Distribution of Media Types</h3>
                    <img :src="pieChartUrl" alt="Pie Chart">
                </div>
                <div>
                    <h3>Total Posts per Influencer</h3>
                    <img :src="influencerPostsUrl" alt="Influencer Posts Chart">
                </div>
                <div>
                    <h3>Top 5 Influencers by Reach</h3>
                    <img :src="topInfluencersReachUrl" alt="Top Influencers Reach Chart">
                </div>
                <div>
                    <h3>Ad Requests by Status</h3>
                    <img :src="adRequestsStatusUrl" alt="Ad Requests Status Chart">
                </div>
                <div>
                    <h3>Budget Allocation per Sponsor</h3>
                    <img :src="budgetAllocationUrl" alt="Budget Allocation Chart">
                </div>
            </div>
        </div>
    `,
    data() {
            return {
                total_influencers: 0,
                total_sponsors: 0,
                total_campaigns: 0,
                total_posts: 0,
                total_active_campaigns: 0,
                total_inactive_campaigns: 0,
                total_adreqeusts: 0,
                pieChartUrl: '',
                influencerPostsUrl: '',
                topInfluencersReachUrl: '',
                adRequestsStatusUrl: '',
                budgetAllocationUrl: ''
            }
            },
            mounted() {
                fetch('/api/admin/statistics')
                .then(response => response.json())
                .then(data => {
                    
                    this.total_influencers = data.total_influencers;
                    this.total_sponsors = data.total_sponsors;
                    this.total_campaigns = data.total_campaigns;
                    this.total_posts = data.total_posts;
                    this.total_active_campaigns = data.total_active_campaigns;
                    this.total_inactive_campaigns = data.total_inactive_campaigns;
                    this.pieChartUrl = data.pie_chart_url;
                    this.influencerPostsUrl = data.influencer_posts_url;
                    this.topInfluencersReachUrl = data.top_influencers_reach_url;
                    this.adRequestsStatusUrl = data.ad_requests_status_url;
                    this.budgetAllocationUrl = data.budget_allocation_url;
                    this.total_adreqeusts = data.total_adreqeusts;
                    
                });
            },
            methods: {
            }
    };

const Sponsors = {
    template: `
        <div>
            <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead class="bg-gray-800 text-white">
                    <tr class="text-left text-sm">
                        <th class="py-3 px-4 uppercase font-semibold">Company Name</th>
                        <th class="py-3 px-4 uppercase font-semibold">Industry</th>
                        <th class="py-3 px-4 uppercase font-semibold">Budget</th>
                        <th class="py-3 px-4 uppercase font-semibold">Actions</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    <tr v-for="sponsor in sponsors" :key="sponsor.id">
                        <td class="py-3 px-4">{{ sponsor.company_name }}</td>
                        <td class="py-3 px-4">{{ sponsor.industry }}</td>
                        <td class="py-3 px-4">{{ sponsor.budget }}</td>
                        <td class="py-3 px-4">
                            <button v-if="sponsor.approval === 0" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2">
                                <a :href="'/approve/' + sponsor.id">Approve</a>
                            </button>

                            <button v-else class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded ml-2">
                                Approved!
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    data() {
        return {
            sponsors: []
        }
    },
    mounted() {
        fetch('/api/sponsors')
            .then(response => response.json())
            .then(data => {
                console.log(data);
                this.sponsors = data;
            });
    },
    methods: {
        deleteSponsor(id) {
            alert('Delete sponsor with ID: ' + id);
        }
    }
};

const Influencers = {
    template: `
        <div>
            <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead class="bg-gray-800 text-white">
                    <tr class="text-left text-sm">
                        <th class="py-3 px-4 uppercase font-semibold">Name</th>
                        <th class="py-3 px-4 uppercase font-semibold">Category</th>
                        <th class="py-3 px-4 uppercase font-semibold">Niche</th>
                        <th class="py-3 px-4 uppercase font-semibold">Reach</th>
                        <th class="py-3 px-4 uppercase font-semibold">Actions</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    <tr v-for="influencer in influe" :key="influencer.id">
                        <td class="py-3 px-4">{{ influencer.name }}</td>
                        <td class="py-3 px-4">{{ influencer.category }}</td>
                        <td class="py-3 px-4">{{ influencer.niche }}</td>
                        <td class="py-3 px-4">{{ influencer.reach }}</td>
                        
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    data() {
        return {
            influe: []
        }
    },
    mounted() {
        fetch('/api/influencers')
            .then(response => response.json())
            .then(data => {
                this.influe = data;
            });
    },
    methods: {
        
    }
};

const Campaigns = {
    template: `
        <div>
            <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead class="bg-gray-800 text-white">
                    <tr class="text-left text-sm">
                        <th class="py-3 px-4 uppercase font-semibold">Name</th>
                        <th class="py-3 px-4 uppercase font-semibold">Description</th>
                        <th class="py-3 px-4 uppercase font-semibold">Start Date</th>
                        <th class="py-3 px-4 uppercase font-semibold">End Date</th>
                        <th class="py-3 px-4 uppercase font-semibold">Budget</th>
                        <th class="py-3 px-4 uppercase font-semibold">Goals</th>
                        <th class="py-3 px-4 uppercase font-semibold">Actions</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    <tr v-for="campaign in campaigns" :key="campaign.id">
                        <td class="py-3 px-4">{{ campaign.name }}</td>
                        <td class="py-3 px-4">{{ campaign.description }}</td>
                        <td class="py-3 px-4">{{ campaign.start_date }}</td>
                        <td class="py-3 px-4">{{ campaign.end_date }}</td>
                        <td class="py-3 px-4">{{ campaign.budget }}</td>
                        <td class="py-3 px-4">{{ campaign.goals }}</td>
                        <td class="py-3 px-4">
                            <button v-if="!campaign.inappropriate" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2" @click="markInappropriate(campaign.id)">
                                Mark Inappropriate
                            </button>
                            <button v-else class="bg-green-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2">
                                Flagged
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    data() {
        return {
            campaigns: []
        }
    },
    mounted() {
        fetch('/api/campaigns')
            .then(response => response.json())
            .then(data => {
                this.campaigns = data;
            });
    },
    methods: {
        markInappropriate(id) {
            fetch(`/api/campaigns/${id}/inappropriate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while marking the campaign as inappropriate.');
            });
        }
    }
};

const Posts = {
    template: `
        <div>
            <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead class="bg-gray-800 text-white">
                    <tr class="text-left text-sm">
                        <th class="py-3 px-4 uppercase font-semibold">Description</th>
                        <th class="py-3 px-4 uppercase font-semibold">Likes</th>
                        <th class="py-3 px-4 uppercase font-semibold">Comments</th>
                        <th class="py-3 px-4 uppercase font-semibold">Actions</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    <tr v-for="post in posts" :key="post.id">
                        <td class="py-3 px-4">{{ post.description }}</td>
                        <td class="py-3 px-4">{{ post.likes }}</td>
                        <td class="py-3 px-4">{{ post.comments }}</td>
                        <td class="py-3 px-4">
                            <button v-if="!post.inappropriate" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2" @click="markInappropriate(post.id)">
                                In appropriate
                            </button>
                            <button v-else class="bg-green-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2">
                                Flagged
                            </button>

                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    data() {
        return {
            posts: []
        }
    },
    mounted() {
        fetch('/api/posts')
            .then(response => response.json())
            .then(data => {
                this.posts = data;
            });
    },
    methods: {
        markInappropriate(id) {
            fetch(`/api/posts/${id}/inappropriate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while marking the campaign as inappropriate.');
            });
        }
    }
};

// Vue Router Setup
const router = new VueRouter({
    routes: [
        { path: '/dashboard', component: Dashboard },
        { path: '/sponsors', component: Sponsors },
        { path: '/influencers', component: Influencers },
        { path: '/campaigns', component: Campaigns },
        { path: '/posts', component: Posts },
        { path: '*', redirect: '/dashboard' }
    ]
});

new Vue({
    el: '#app',
    router,
    render: h => h(AdminDashboard)
});