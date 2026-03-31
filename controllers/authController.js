const token = jwt.sign(
  { id: user.id, phone: user.phone, name: user.name, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: '7d' }
);

res.json({
  success: true,
  token,
  user: {
    id: user.id,
    name: user.name,
    phone: user.phone,
    role: user.role,
    matricule: user.matricule
  }
});
