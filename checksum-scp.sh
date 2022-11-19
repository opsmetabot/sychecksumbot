#/bin/sh
#1  cp local file to local file  pass
#2  cp local file to local dir  pass
#3  cp local dir to local dir   pass 
#4  cp remote file to local dir
#5  cp remote file to local file
#6  cp remote dir to local dir
#7  cp local file to remote file
#8  cp local file to remote dir
#9  cp local dir to remote dir
#10  cp remote file to remote file
#11 cp remote file to remote dir
#12  cp remote dir to remote dir

usage(){
   echo 'cychecksum-local.sh [OPTION] <src:pi@kunsh04:/path/to/from> <tar:pi@kunsh05:/path/to/target>'
   echo 'OPTION'
   echo '   -s      - sanity to ssh connect'
   echo '   -r      - same with scp -r'
   exit -1
}

if [ ! $2 ];then 
   usage
fi 


## check options
from_path=
target_path=
#opts
check_sanity_opt=
cp_dir_opt=
#loop
for opt in $@;do
   if [ "$opt" = "-h" ];then 
      usage
   elif [ "$opt" = "-c" ];then
      check_sanity_opt=$opt
   elif [ $opt = '-r' ];then
      cp_dir_opt=$opt
   elif [ $from_path ];then
      target_path=$opt
   else 
      from_path=$opt     
   fi
done

## main
local_file_local_file(){
    from=$1
    target=$2

    ## if target not exits
    if [ ! -f $target ];then
        ## get path
        t_path=${target%/*}
        if [ ! -d t_path ];then
           mkdir -p $t_path
        fi
        cp $from $target
        exit
    fi

    checksum=$(md5sum $from)
    sum=${checksum% *}
    t_checksum=$(md5sum $target)
    t_sum=${t_checksum% *}
    if [ "$sum" = "$t_sum" ];then
        ## skip
        echo skip! $from $target
    else
        cp $from $target
    fi
}

cp_local_file_local_file(){
   local_file_local_file $from_path $target_path 
}

cp_local_file_local_dir(){
   checksum=$(md5sum $from_path)
   sum=${checksum% *}
   filename=${from_path##*\/} 
   t_path="$target_path/$filename"
   t_checksum=$(md5sum $t_path)
   t_sum=${t_checksum% *}
   if [ "$sum" = "$t_sum" ];then
       ## skip
       echo skip! $from_path $target_path
   else
       cp $from_path $target_path
   fi
}

cp_local_dir_local_dir(){
    list=$(find $from_path -type f )
    for it in ${list[@]};do
        relative_path=${it#$from_path} 
        relative_path=${relative_path#\/}
        new_path=${target_path%\/}
        new_path="$new_path/$relative_path"

        ## cp file to file
        local_file_local_file  $it  $new_path
    done
}


## cp file to file
if [ -f $from_path -a -f $target_path ];then
   cp_local_file_local_file
   exit
elif [ -f $from_path -a -d $target_path ];then
   cp_local_file_local_dir
   exit
elif [ -d $from_path -a -d $target_path ];then
   cp_local_dir_local_dir
   exit
fi



##  below for remote sync

parse_ssh_path(){
    line=$1
    path=${line#*:}
    echo $path
}

parse_ssh_host(){
    line=$1
    path=${line#*:}
    host=${line%:*}
    if [ "$host" = "$path" ];then
       unset host
    fi

    echo $host
}


check_sanity(){
   local from=$1
   local target=$2

   local host=$(parse_ssh_host $from)
   if [ $host ];then
      ssh $host ls
   fi

   ## target
   host=$(parse_ssh_host $target)
   if [ $host ];then
      ssh $host ls
   fi
}


if [ ! $target_path ];then
   usage
elif [ $check_sanity_opt ];then 
   check_sanity $from_path $target_path
   exit
fi

print_checksum_files(){
   line=$1
   ## dir or file
   dir_or_not=$2
   if [ -d $line ];then 
      dir_or_not=$line
   fi

   host=$(parse_ssh_host $line)
   path=$(parse_ssh_path $line)

   #check empty
   if [ -z "$(ls $path)" ];then
      return 
   fi

   local run_bin=
   if [ $dir_or_not ];then
      ## relative path
      run_bin="cd $path && find -type f -not -path $path | xargs md5sum"

      # TODO
      # repl=$(echo $path | sed -e 's/\//\\\//g')
      # find $path -type f | sed -e "s/$repl//"
      
   elif [ -f $path ];then
      ## abs path, convert to realtive path
      local t_path=${path%/*}
      local t_file=${path##*/}
      t_file="./$t_file"
      cd $t_path
      run_bin="md5sum $t_file"
   fi

   if [ $host ];then
   #    echo ssh $host "\"$run_bin\""
      ssh $host "$run_bin"
   else
      eval $run_bin
   fi
}


## declare two hash
declare -A from_hash
declare -A target_hash

## create the hash from input lines
create_from_hash(){
    local _lines=("$@")
    # for line in ${_lines[@]};do
    #   echo hash_line=$line
    # done

    local new_line=
    for line in ${_lines[@]};do
       if [ $new_line ];then
          from_hash[$line]=$new_line
          unset new_line
       else 
          new_line=$line  #checksum
       fi
    done
    
    # for i in "${!from_hash[@]}";do
    #     echo "key  : $i"
    #     echo "value: ${from_hash[$i]}"
    # done
}
## create the hash from input lines
create_target_hash(){
    local _lines=("$@")
    # for line in ${_lines[@]};do
    #   echo hash_line=$line
    # done

    local new_line=
    for line in ${_lines[@]};do
       if [ $new_line ];then
          target_hash[$line]=$new_line
          unset new_line
       else 
          new_line=$line  #checksum
       fi
    done
    
    # for i in "${!target_hash[@]}";do
    #     echo "key  : $i"
    #     echo "value: ${target_hash[$i]}"
    # done
}

# create hash from array
unset lines
for line in $(print_checksum_files $from_path $cp_dir_opt);do
    lines+=($line)
done
create_from_hash ${lines[@]}

unset lines
for line in $(print_checksum_files $target_path $cp_dir_opt);do
    lines+=($line)
done
create_target_hash ${lines[@]}
## print
# for i in "${!from_hash[@]}";do
#     echo "key  : $i"
#     echo "value: ${from_hash[$i]}"
# done
# for i in "${!target_hash[@]}";do
#     echo "key  : $i"
#     echo "value: ${target_hash[$i]}"
# done

sync_checksum(){
    local syncing=$1
    local checksum=$2

    # TODO, check ssh 
    
    # echo scp $from_path/$syncing  $target_path
    cp $syncing  $target_path

}

print_not_match_files(){
    local checksum=
    for i in "${!from_hash[@]}";do
        checksum=${from_hash[$i]}
        t_CHECKSUM=${target_hash[$i]}

        if [ "$checksum" != "$t_CHECKSUM" ];then
           sync_checksum $i $t_CHECKSUM
        #else
           #echo skip  $i $checksum
        fi
    done
}


## final process checksum
# declare -p $from_hash
# declare -p $target_hash
print_not_match_files
