from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def r_categories(categories, selected_category, request, depth=0):
  """
  Recursively renders collapsible nested categories while preserving active search strings.
  """
  html = ""
  indent = depth * 25

  search_query = request.GET.get('q', '')
  search_param = f"&q={search_query}" if search_query else ""

  for cat in categories:
    has_children = cat.children.exists()
    is_active = selected_category and selected_category.id == cat.id
    
    active_classes = "text-larp-gold font-semibold bg-larp-dark/30" if is_active else "text-larp-light/70 hover:text-larp-light hover:bg-larp-dark/20"
    
    html += f'''
    <div class="category-node w-full">
      <div style="padding-left: {max(12, indent)}px;" 
           class="flex items-center justify-between group rounded transition-colors {active_classes}">
        
        <a href="?category={cat.slug}{search_param}" class="flex-grow py-2 text-xs uppercase tracking-wide truncate">
          {cat.name}
        </a>
    '''

    if has_children:
      html += f'''
        <button onclick="toggleCategoryBranch(this)" 
                class="category-toggle-btn p-2 text-larp-copper/60 hover:text-larp-gold transition-transform duration-150 focus:outline-none" 
                aria-label="Toggle {cat.name} subcategories">
          <i class="fa-solid fa-chevron-down text-[10px]"></i>
        </button>
      '''
    else:
      html += '''
        <span class="text-[9px] opacity-20 group-hover:opacity-60 pr-3.5 font-mono">&rarr;</span>
      '''

    html += '</div>' # End of node header row

    if has_children:
      start_hidden = "hidden" if not selected_category else ""
      
      html += f'<div class="category-children-block border-l border-larp-copper/10 ml-2 space-y-1 mt-1 {start_hidden}">'
      html += r_categories(cat.children.all(), selected_category, request, depth + 1)
      html += '</div>'

    html += '</div>' # End of category node wrapper

  return mark_safe(html)