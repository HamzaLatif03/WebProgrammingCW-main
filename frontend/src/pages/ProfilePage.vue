<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow-sm">
          <div class="card-header">
            <h2 class="text-center mb-0">My profile</h2>
          </div>
          
          <div v-if="authStore.isAuthenticated" class="card-body">
            <form @submit.prevent="saveProfile">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input 
                  type="text"
                  name="username"
                  class="form-control"
                  v-model="profile.username" 
                  required 
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Name</label>
                <input 
                  type="text" 
                  name="name"
                  class="form-control"
                  v-model="profile.name" 
                  required 
                />
              </div>

              <div class="mb-3">
                <label class="form-label">E-mail</label>
                <input 
                  type="email"
                  name="email"
                  class="form-control"
                  v-model="profile.email" 
                  required 
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Date of birth</label>
                <input 
                  type="date"
                  name="date_of_birth"
                  class="form-control"
                  v-model="profile.date_of_birth" 
                  required 
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Hobbies</label>
                <div class="mb-2">
                  <span 
                    v-for="hobby in profile.hobbies" 
                    :key="hobby.id"
                    class="badge bg-primary me-2 mb-2"
                  >
                    {{ hobby.hobby_name }}
                    <button 
                      type="button" 
                      class="btn-close btn-close-white ms-2"
                      @click="removeHobby(hobby)"
                      aria-label="Remove hobby"
                    ></button>
                  </span>
                </div>
                <div class="input-group">
                  <input
                    type="text" 
                    class="form-control"
                    v-model="newHobby" 
                    placeholder="Type to search or add new hobby"
                
                  />
                  <button 
                    type="button" 
                    class="btn btn-outline-primary"
                    @click="handleHobbyInput(newHobby)"
                  >
                    {{ filteredHobbies.length ? 'Add Selected' : 'Create New' }}
                  </button>
                </div>
                <div v-if="newHobby" class="list-group mt-2">
                  <div class="small text-muted mb-1">
                    {{ filteredHobbies.length ? 'Existing hobbies:' : 'No matching hobbies found. Click Create New to add.' }}
                  </div>
                  <button 
                    v-for="hobby in filteredHobbies" 
                    :key="hobby.id"
                    type="button"
                    class="list-group-item list-group-item-action"
                    @click="selectHobby(hobby)"
                  >
                    {{ hobby.hobby_name }}
                  </button>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Change password</label>
                <input 
                  type="password"
                  name="password"
                  class="form-control"
                  v-model="passwordInput"
                  placeholder="New password (leave empty to keep current)"
                />
              </div>

              <button type="submit" class="btn btn-primary w-100">
                Save changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import type { User, Hobby } from '../types';
import { useHobbyStore} from '../store/hobby_store';
import { useUserStore} from '../store/user_store';
import { useAuthStore } from '../store/auth';

export default defineComponent({
  name: 'ProfilePage',
  setup() {
    const profile = ref<User>({
      id: 0,
      name: '',
      username:'',
      password: '',
      email: '',
      date_of_birth: '',
      hobbies: [],
      friends: [],
    });
    
    const passwordInput = ref<string>('');
    const newHobby = ref('');
    
    const hobbyStore = useHobbyStore();
    const userStore = useUserStore();
    const authStore = useAuthStore();

    const filteredHobbies = computed(() => {
      if (!newHobby.value) return [];
      const searchTerm = newHobby.value.toLowerCase();
      return hobbyStore.hobbies.filter(hobby => 
        hobby.hobby_name.toLowerCase().includes(searchTerm) &&
        !profile.value.hobbies.some(h => h.id === hobby.id)
      );
    });

    const handleHobbyInput = async(newHobby: string) => {
      
      if (!newHobby.trim()) return;

      if (filteredHobbies.value.length) {
        selectHobby(filteredHobbies.value[0]);        
        return;
      }
      try{
        await hobbyStore.addHobby({ hobby_name: newHobby });
      }
      finally{
        profile.value.hobbies.push(hobbyStore.hobbies[hobbyStore.hobbies.length - 1]);
      }
      newHobby = '';

    }

    const selectHobby = (hobby: Hobby) => {
      profile.value.hobbies.push(hobby);
      newHobby.value = '';
    };

    const removeHobby = (hobby: Hobby) => {
      profile.value.hobbies = profile.value.hobbies.filter(h => h.id !== hobby.id);
    };

    const saveProfile = async () => {
      try {
        const userData = {
          ...profile.value,
          
        };
        if (passwordInput.value.trim() !== '') {
          userData.password = passwordInput.value;
        }
        console.log(userData.password);
        console.log('Sending update:', userData);
        await userStore.updateProfile(userData);
        alert('Profile updated successfully!');
        passwordInput.value = '';
        console.log('Update complete');
      } catch (error) {
        console.error('Error updating profile:', error);
      }
    };

    onMounted(async () => {
      await authStore.fetchUser();
      if (authStore.isAuthenticated) {
        await Promise.all([
          userStore.fetchCurrentUser(),
          hobbyStore.fetchHobbies()
        ]);
        if (userStore.currentUser) {
          profile.value = { ...userStore.currentUser };
        }
      }
    });

    return {
      profile,
      newHobby,
      passwordInput,
      filteredHobbies,
      authStore,
      saveProfile,
      handleHobbyInput,
      selectHobby,
      removeHobby,
    };
  },
});
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hobbies-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.selected-hobbies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hobby-tag {
  background-color: #e0e0e0;
  padding: 4px 8px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.remove-hobby {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 4px;
}

.hobby-suggestions {
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.hobby-suggestion:hover {
  background-color: #f5f5f5;
}
</style>

