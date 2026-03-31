const Student = require('../models/Student');

// Parent : récupérer ses élèves
exports.getMyStudents = async (req, res) => {
    try {
        const students = await Student.findByParent(req.user.id);
        res.json(students);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des élèves' });
    }
};

// Admin : récupérer tous les élèves
exports.getAllStudents = async (req, res) => {
    try {
        const students = await Student.getAll();
        res.json(students);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des élèves' });
    }
};

// Admin : ajouter un élève (avec parent existant)
exports.addStudentByAdmin = async (req, res) => {
    const { name, class_id, matricule, parent_phone, school_fees } = req.body;
    try {
        const student = await Student.adminCreate({ name, class_id, matricule, parent_phone, school_fees });
        res.json(student);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
};

// Parent : ajouter un élève (création de compte parent déjà existant)
exports.addMyStudent = async (req, res) => {
    const { name, class_id, matricule, school_fees } = req.body;
    try {
        const student = await Student.create({
            parent_id: req.user.id,
            name,
            class_id,
            matricule,
            school_fees
        });
        res.json(student);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de l’ajout de l’élève' });
    }
};
