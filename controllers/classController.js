const Class = require('../models/Class');

exports.getAllClasses = async (req, res) => {
    try {
        const classes = await Class.getAll();
        res.json(classes);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des classes' });
    }
};

exports.createClass = async (req, res) => {
    const { name, level, cycle, school_fees } = req.body;
    try {
        const newClass = await Class.create({ name, level, cycle, school_fees });
        res.json(newClass);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la création de la classe' });
    }
};

exports.updateClass = async (req, res) => {
    const { id } = req.params;
    const { name, level, cycle, school_fees } = req.body;
    try {
        const updated = await Class.update(id, { name, level, cycle, school_fees });
        if (!updated) return res.status(404).json({ error: 'Classe non trouvée' });
        res.json(updated);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la mise à jour' });
    }
};

exports.deleteClass = async (req, res) => {
    const { id } = req.params;
    try {
        await Class.delete(id);
        res.json({ success: true });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la suppression' });
    }
};
