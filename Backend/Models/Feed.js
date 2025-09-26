const mongoose = require("mongoose");

const CommentSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  content: { type: String, required: true },
  likes: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }],
}, { timestamps: true });

const FeedSchema = new mongoose.Schema({
  author: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  content: { type: String, required: true },
  type: {
    type: String,
    enum: ["post", "doubt", "course", "achievement", "project-showcase"],
    default: "post",
  },
  tags: [String],
  category: { type: String },
  media: [{
    type: { type: String, enum: ["image", "video", "document"] },
    url: { type: String, required: true },
    caption: { type: String },
  }],
  likes: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }],
  comments: [CommentSchema],
  shares: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }],
  savedBy: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }],
  isPublic: { type: Boolean, default: true },
  isPinned: { type: Boolean, default: false },
  
  // For doubts
  isResolved: { type: Boolean, default: false },
  bestAnswer: { type: mongoose.Schema.Types.ObjectId, ref: "Comment" },
  
  // For courses
  difficulty_level: { 
    type: String, 
    enum: ["beginner", "intermediate", "advanced"], 
    default: "beginner" 
  },
  complexity_score: { type: Number, min: 1, max: 10 },
  duration: { type: Number }, // in minutes
  summary: { type: String },
  keywords: [String],
  additional_tags: [String],
  
  // Analytics
  views: { type: Number, default: 0 },
  engagement: { type: Number, default: 0 },
}, { timestamps: true });

// Index for better performance
FeedSchema.index({ author: 1, createdAt: -1 });
FeedSchema.index({ type: 1, createdAt: -1 });
FeedSchema.index({ tags: 1 });
FeedSchema.index({ category: 1 });

// Index specifically for courses
FeedSchema.index({ complexity_score: 1 });
FeedSchema.index({ difficulty_level: 1 });
FeedSchema.index({ keywords: 1 });

module.exports = mongoose.model("Feed", FeedSchema);
