<template>
  <div class="container-fluid mt-5">
    <h2 class="text-center mb-4">Users with Similar Hobbies</h2>
    
    <div class="row">
      <!-- Left Column: Filter -->
      <div class="col-md-3">
        <!-- Age Filter -->
        <div class="card shadow-sm mb-4">
          <div class="card-header">
            <h4 class="text-center mb-0">Filter</h4>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Min age</label>
              <input 
                type="number" 
                class="form-control"
                name="minAge"
                v-model="minAge" 
                min="0"
                max="120"
              />
            </div>
            <div class="mb-4">
              <label class="form-label">Max age</label>
              <input 
                type="number" 
                class="form-control"
                name="maxAge"
                v-model="maxAge" 
                min="0"
                max="120"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: User List -->
      <div class="col-md-6">
        <!-- Pagination Buttons -->
        <div class="d-flex justify-content-center mt-4 mb-4">
          <button
            name="previousPage"
            :disabled="page <= 1"
            class="btn btn-primary btn-sm me-2"
            @click="changePage(page - 1)"
          >
            Previous Page
          </button>

          <button class="btn btn-primary btn-sm">
            {{ page }}
          </button>

          <button
            name="nextPage"
            :disabled="page >= totalPages"
            class="btn btn-primary btn-sm ms-2"
            @click="changePage(page + 1)"
          >
            Next Page
          </button>
        </div>

        <div v-if="authStore.isAuthenticated" class="row row-cols-1 row-cols-md-2 g-4">
          <div v-for="user in filteredUsers" 
               :key="user.id" 
               class="col">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h5 class="card-title">{{ user.name }}</h5>
                <p class="text-gray-600">
                  Age: {{ new Date().getFullYear() - new Date(user.date_of_birth).getFullYear() }}
                </p>
                <!-- Shared Hobbies Count -->
                <div class="mb-2">
                  <h6 class="font-medium">Shared Hobbies:</h6>
                  <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {{ user.shared_hobbies_count }}
                  </span>
                </div>

                <!-- Hobbies List -->
                <div class="mb-3">
                  <h6 class="mb-2">Hobbies:</h6>
                  <div class="d-flex flex-wrap">
                    <span 
                      v-for="hobby in user.hobbies" 
                      :key="hobby.id"
                      class="badge bg-primary px-3 py-1.5 rounded-pill me-2 mb-2"
                    >
                      {{ hobby.hobby_name }}
                    </span>
                  </div>
                </div>

                <!-- Friend Request Button -->
                <div class="mt-3">
                  <button 
                    v-if="!isFriend(user.id) && !hasPendingRequest(user.id)"
                    @click="sendFriendRequest(user.id)"
                    class="btn btn-primary w-full"
                  >
                    Send Friend Request
                  </button>
                  <button 
                    v-else-if="hasPendingRequest(user.id)"
                    class="btn btn-secondary w-full" 
                    disabled
                  >
                    Request Pending
                  </button>
                  <div 
                    v-else
                    class="btn btn-success w-full" 
                    style="cursor: default;"
                  >
                    Already Friends
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Friend Requests and Friends List -->
      <div class="col-md-3">
        <!-- Friend Requests -->
        <div class="card shadow-sm mb-4">
          <div class="card-header">
            <h4 class="text-center mb-0">Friend Requests</h4>
          </div>
          <div class="card-body">
            <div v-for="request in pendingRequests" :key="request.id" class="mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <span>{{ request.sender.name }}</span>
                <div>
                  <button 
                    class="btn btn-success btn-sm me-2"
                    @click="handleFriendRequest(request.id, 'accepted')"
                  >
                    Accept
                  </button>
                  <button 
                    class="btn btn-danger btn-sm"
                    @click="handleFriendRequest(request.id, 'rejected')"
                  >
                    Reject
                  </button>
                </div>
              </div>
            </div>
            <div v-if="pendingRequests.length === 0" class="text-center text-muted">
              No pending requests
            </div>
          </div>
        </div>

        <!-- My Friends -->
        <div class="card shadow-sm">
          <div class="card-header">
            <h4 class="text-center mb-0">My Friends</h4>
          </div>
          <div class="card-body">
            <div v-for="friend in friends" :key="friend.id" class="mb-3">
              <div class="p-3 border rounded">
                <h6 class="mb-2">{{ friend.name }}</h6>
                <div class="d-flex align-items-center">
                  <span class="me-2">Shared Hobbies:</span>
                  <span class="badge bg-primary">{{ friend.shared_hobbies_count }}</span>
                </div>
              </div>
            </div>
            <div v-if="friends.length === 0" class="text-center text-muted">
              No friends yet
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../store/auth'
import { useSimilarUsersStore } from '../store/similar_users_store'
import { useFriendStore } from '../store/friend_store'

export default defineComponent({
  setup() {
    const authStore = useAuthStore()
    const similarUsersStore = useSimilarUsersStore()
    const friendStore = useFriendStore()
    const minAge = ref(0)
    const maxAge = ref(100)
    const page = ref(1) 

    const filteredUsers = computed(() => {
      return similarUsersStore.similarUsers
    })
    const totalPages = computed(() => {
      return similarUsersStore.totalPages
    })

    const hasPendingRequest = (userId) => {
      return friendStore.relationships.some(r => 
        ((r.sender.id === friendStore.currentUserId && r.receiver.id === userId) ||
         (r.receiver.id === friendStore.currentUserId && r.sender.id === userId)) &&
        r.status === 'pending'
      )
    }

    
    const changePage = (newPage) => {
      page.value = newPage
      similarUsersStore.fetchSimilarUsers(minAge.value, maxAge.value, newPage)
    }
    
    watch([minAge, maxAge], async ([newMinAge, newMaxAge]) => {
      await similarUsersStore.fetchSimilarUsers(newMinAge, newMaxAge, page.value);
    });

    const friends = computed(() => {
      return friendStore.relationships
        .filter(r => 
          ((r.sender.id === friendStore.currentUserId) || 
          (r.receiver.id === friendStore.currentUserId)) &&
          r.status === 'accepted'
        )
        .map(r => {
          const friendUser = r.sender.id === friendStore.currentUserId ? r.receiver : r.sender;
          const userWithHobbies = similarUsersStore.similarUsers.find(u => u.id === friendUser.id);
          return {
            ...friendUser,
            shared_hobbies_count: userWithHobbies ? userWithHobbies.shared_hobbies_count : 0
          };
        });
    })

    const sendFriendRequest = async (userId) => {
      if (hasPendingRequest(userId)) {
        return 
      }
      try {
        await friendStore.sendFriendRequest(userId)
      } catch (error) {
        console.error('Failed to send friend request:', error)
      }
    }

    const pendingRequests = computed(() => {
      return friendStore.relationships.filter(r => 
        r.receiver.id === friendStore.currentUserId && 
        r.status === 'pending'
      )
    })

    const handleFriendRequest = async (relationshipId, status) => {
      try {
        await friendStore.updateFriendRequest(relationshipId, status)
        await friendStore.fetchRelationships()
      } catch (error) {
        console.error('Failed to update friend request:', error)
      }
    }

    const isFriend = (userId) => {
      return friendStore.relationships.some(r => 
        ((r.sender.id === friendStore.currentUserId && r.receiver.id === userId) ||
         (r.receiver.id === friendStore.currentUserId && r.sender.id === userId)) &&
        r.status === 'accepted'
      )
    }

    onMounted(async () => {
      await Promise.all([authStore.fetchUser(), similarUsersStore.fetchSimilarUsers(minAge.value, maxAge.value, page.value), friendStore.fetchRelationships()])
    })

    return {
      authStore,
      friendStore,
      filteredUsers,
      friends,
      minAge,
      maxAge,
      page,
      totalPages,
      hasPendingRequest,
      sendFriendRequest,
      pendingRequests,
      handleFriendRequest,
      isFriend,
      changePage,
    }
  }
})
</script>
