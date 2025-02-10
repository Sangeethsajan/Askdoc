import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export const useUser = () => {
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedUserId = localStorage.getItem('askdoc_user_id');
    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      const newUserId = uuidv4();
      localStorage.setItem('askdoc_user_id', newUserId);
      setUserId(newUserId);
    }
    setIsLoading(false);
  }, []);
  return { userId, isLoading };
};