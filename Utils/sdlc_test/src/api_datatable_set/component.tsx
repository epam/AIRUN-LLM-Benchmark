import React, { useEffect, useState, ChangeEvent } from 'react';
import ClipLoader from 'react-spinners/ClipLoader';

// Define the user type
interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  status: string;
}

const DataTableComponent: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [search, setSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/users');
        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }
        const data = await response.json();
        setUsers(data);
      } catch (err: any) {
        setError(err.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  // Get unique roles and statuses for dropdowns
  const roles = Array.from(new Set(users.map((u) => u.role)));
  const statuses = Array.from(new Set(users.map((u) => u.status)));

  // Filtered users
  const filteredUsers = users.filter((user) => {
    const matchesSearch = user.name.toLowerCase().includes(search.toLowerCase());
    const matchesRole = roleFilter ? user.role === roleFilter : true;
    const matchesStatus = statusFilter ? user.status === statusFilter : true;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const handleClearFilters = () => {
    setSearch('');
    setRoleFilter('');
    setStatusFilter('');
  };

  if (loading) {
    return (
      <div data-testid="loading">
        <ClipLoader data-testid="loader" />
        Loading...
      </div>
    );
  }

  if (error) {
    return <div data-testid="loading">Error: {error}</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <input
          data-testid="search-input"
          type="text"
          placeholder="Search by name"
          value={search}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          style={{ marginRight: 8 }}
        />
        <select
          data-testid="role-filter"
          value={roleFilter}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => setRoleFilter(e.target.value)}
          style={{ marginRight: 8 }}
        >
          <option value="">All Roles</option>
          {roles.map((role) => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
        <select
          data-testid="status-filter"
          value={statusFilter}
          onChange={(e: ChangeEvent<HTMLSelectElement>) => setStatusFilter(e.target.value)}
          style={{ marginRight: 8 }}
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
        <button data-testid="clear-filters" onClick={handleClearFilters}>
          Clear Filters
        </button>
      </div>
      <table data-testid="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTableComponent;
