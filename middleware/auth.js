const decoded = jwt.verify(token, process.env.JWT_SECRET);
req.user = {
  id: decoded.id,
  phone: decoded.phone,
  name: decoded.name,
  role: decoded.role
};
