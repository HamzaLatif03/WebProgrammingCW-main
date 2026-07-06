export interface Hobby {
    id: number;
    hobby_name: string;
  }
  
  export interface User {
    id: number;
    name: string;
    username: string;
    password: string;
    email: string;
    date_of_birth: string | null;
    hobbies: Hobby[];
    friends: number[];
  }
  
  export interface UserHobby {
    id: number;
    hobby: {
      id: number;
      name: string;
    };
    user: {
      id: number;
      name: string;
    };
  }
  
  export interface FriendRelationship {
    id: number;
    sender: {
      id: number;
      name: string;
    };
    receiver: {
      id: number;
      name: string;
    };
    status: 'pending' | 'accepted' | 'rejected';
    created_at: string;
  }