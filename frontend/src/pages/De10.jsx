import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Button } from '../components/ui/button';
import { Plus, Pencil, Trash2, Dices } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const De10 = () => {
  const [lists, setLists] = useState([]);
  const [selectedLists, setSelectedLists] = useState([]);
  const [result, setResult] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingList, setEditingList] = useState(null);
  const [formData, setFormData] = useState({ name: '', items: Array(10).fill('') });
  const { toast } = useToast();

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    try {
      const response = await axios.get(`${API}/de10lists`);
      setLists(response.data);
    } catch (error) {
      console.error('Error fetching lists:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingList) {
        await axios.put(`${API}/de10lists/${editingList._id}`, formData);
        toast({ title: 'Liste mise à jour' });
      } else {
        await axios.post(`${API}/de10lists`, formData);
        toast({ title: 'Liste ajoutée' });
      }
      fetchLists();
      setIsDialogOpen(false);
      setFormData({ name: '', items: Array(10).fill('') });
      setEditingList(null);
    } catch (error) {
      toast({ variant: 'destructive', title: 'Erreur' });
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette liste ?')) {
      try {
        await axios.delete(`${API}/de10lists/${id}`);
        toast({ title: 'Liste supprimée' });
        fetchLists();
        setSelectedLists(selectedLists.filter(listId => listId !== id));
      } catch (error) {
        toast({ variant: 'destructive', title: 'Erreur' });
      }
    }
  };

  const rollDice = () => {
    if (selectedLists.length === 0) {
      toast({ variant: 'destructive', title: 'Sélectionnez au moins une liste' });
      return;
    }

    // Collecter toutes les options des listes sélectionnées
    const allOptions = [];
    selectedLists.forEach(listId => {
      const list = lists.find(l => l._id === listId);
      if (list) {
        list.items.forEach((item, index) => {
          if (item && item.trim()) {
            allOptions.push({
              listName: list.name,
              number: index + 1,
              text: item
            });
          }
        });
      }
    });

    if (allOptions.length === 0) {
      toast({ variant: 'destructive', title: 'Aucune option dans les listes sélectionnées' });
      return;
    }

    const randomIndex = Math.floor(Math.random() * allOptions.length);
    setResult(allOptions[randomIndex]);
  };

  const toggleListSelection = (listId) => {
    setSelectedLists(prev =>
      prev.includes(listId)
        ? prev.filter(id => id !== listId)
        : [...prev, listId]
    );
  };

  const openEditDialog = (list) => {
    setEditingList(list);
    setFormData({ name: list.name, items: [...list.items] });
    setIsDialogOpen(true);
  };

  const updateItem = (index, value) => {
    const newItems = [...formData.items];
    newItems[index] = value;
    setFormData({ ...formData, items: newItems });
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <h1 className="text-3xl font-serif text-white">Dé 10</h1>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={() => {
                  setEditingList(null);
                  setFormData({ name: '', items: Array(10).fill('') });
                }}
                className="bg-slate-700 hover:bg-slate-600"
              >
                <Plus className="w-4 h-4 mr-2" /> Nouvelle liste
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#0f172a] border-slate-700 max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-white">
                  {editingList ? 'Éditer' : 'Nouvelle'} Liste
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label className="text-white">Nom de la liste</Label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    placeholder="Ex: Tâches ménagères, Punitions..."
                    className="bg-[#1e293b] border-slate-600 text-white placeholder:text-slate-500"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Options (1 à 10)</Label>
                  {formData.items.map((item, index) => (
                    <div key={index} className="flex gap-2 items-center">
                      <span className="text-slate-400 text-sm w-6">{index + 1}.</span>
                      <Input
                        value={item}
                        onChange={(e) => updateItem(index, e.target.value)}
                        placeholder={`Option ${index + 1}`}
                        className="bg-[#1e293b] border-slate-600 text-white placeholder:text-slate-500"
                      />
                    </div>
                  ))}
                </div>
                <Button type="submit" className="w-full bg-slate-700 hover:bg-slate-600">
                  {editingList ? 'Mettre à jour' : 'Ajouter'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Dice Result */}
        {result && (
          <div className="bg-gradient-to-br from-purple-900/40 to-pink-900/40 backdrop-blur-md rounded-lg border border-purple-500/50 p-8 mb-6 text-center animate-in fade-in duration-500">
            <Dices className="w-16 h-16 text-purple-400 mx-auto mb-4" />
            <div className="text-sm text-purple-300 mb-2">{result.listName}</div>
            <h2 className="text-3xl font-bold text-white mb-2">#{result.number}</h2>
            <p className="text-xl text-purple-200">{result.text}</p>
          </div>
        )}

        {/* Roll Button */}
        <div className="text-center mb-8">
          <Button
            onClick={rollDice}
            disabled={selectedLists.length === 0}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-6 text-lg disabled:opacity-50"
          >
            <Dices className="w-6 h-6 mr-2" />
            Lancer le dé
          </Button>
          {selectedLists.length > 0 && (
            <p className="text-slate-400 text-sm mt-2">
              {selectedLists.length} liste(s) sélectionnée(s)
            </p>
          )}
        </div>

        {/* Lists */}
        <div className="space-y-4">
          {lists.length === 0 ? (
            <div className="bg-[#0f172a]/60 backdrop-blur-md rounded-lg border border-slate-700/50 p-8 text-center">
              <p className="text-slate-400">Aucune liste configurée</p>
            </div>
          ) : (
            lists.map((list) => (
              <div
                key={list._id}
                className="bg-[#0f172a]/60 backdrop-blur-md rounded-lg border border-slate-700/50 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={selectedLists.includes(list._id)}
                      onCheckedChange={() => toggleListSelection(list._id)}
                      className="border-slate-600"
                    />
                    <h3 className="text-lg font-semibold text-white">{list.name}</h3>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(list)}
                      className="text-slate-400 hover:text-white"
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(list._id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                  {list.items.map((item, index) => (
                    <div
                      key={index}
                      className="bg-slate-800/50 rounded p-2 border border-slate-700 text-sm"
                    >
                      <span className="text-slate-400">{index + 1}.</span>{' '}
                      <span className="text-slate-200">{item || '—'}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  );
};

export default De10;